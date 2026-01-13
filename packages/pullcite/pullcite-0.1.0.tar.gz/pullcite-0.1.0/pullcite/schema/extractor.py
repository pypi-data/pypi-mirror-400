"""
Schema-aware extractor for Django-style field definitions.

This extractor works with ExtractionSchema classes and uses field-level
search configurations for context gathering and verification.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Type, TypeVar

from .base import ExtractionSchema, Field, SearchType
from ..core.document import Document
from ..core.chunk import Chunk
from ..core.evidence import (
    Evidence,
    EvidenceCandidate,
    VerificationResult,
    VerificationStatus,
)
from ..core.result import (
    ExtractionResult,
    ExtractionStats,
    ExtractionFlag,
    ExtractionFlagType,
    ExtractionStatus,
)
from ..llms.base import LLM, Message, Role, Tool, ToolCall
from ..search.base import Searcher, SearchResult


T = TypeVar("T", bound=ExtractionSchema)


# Type for custom prompt builder callbacks
PromptBuilder = Any  # Callable[[Type[ExtractionSchema], dict[str, list[SearchResult]]], str]


@dataclass
class SchemaExtractor:
    """
    Extractor that uses Django-style schema definitions.

    Unlike the base Extractor, this uses ExtractionSchema with field-level
    search configurations. Each field specifies its own query and search type,
    enabling field-aware context gathering for large documents.

    Attributes:
        schema: ExtractionSchema subclass defining fields to extract.
        llm: Language model for extraction and verification.
        searcher: BM25 or hybrid searcher for field-level search.
        retriever: Optional semantic retriever for semantic/hybrid fields.
        top_k: Number of chunks to retrieve per field. Default 3.
        verify: Whether to verify extracted values. Default True.
        system_prompt: Custom system prompt (replaces default if provided).
        extra_instructions: Additional instructions appended to the prompt.
        prompt_builder: Custom function to build the extraction prompt.
                       Signature: (schema, field_contexts) -> str

    Example:
        >>> from pullcite.schema import (
        ...     SchemaExtractor,
        ...     ExtractionSchema,
        ...     DecimalField,
        ...     StringField,
        ...     SearchType,
        ... )
        >>> from pullcite.search import BM25Searcher
        >>> from pullcite.llms import AnthropicLLM
        >>>
        >>> class Invoice(ExtractionSchema):
        ...     total = DecimalField(
        ...         query="total amount due invoice",
        ...         search_type=SearchType.BM25,
        ...     )
        ...     vendor = StringField(
        ...         query="vendor company name",
        ...         search_type=SearchType.BM25,
        ...     )
        >>>
        >>> # Basic usage
        >>> extractor = SchemaExtractor(
        ...     schema=Invoice,
        ...     llm=AnthropicLLM(),
        ...     searcher=BM25Searcher(),
        ... )
        >>>
        >>> # With custom instructions
        >>> extractor = SchemaExtractor(
        ...     schema=Invoice,
        ...     llm=AnthropicLLM(),
        ...     searcher=BM25Searcher(),
        ...     extra_instructions="Focus on the summary section for totals.",
        ... )
        >>>
        >>> # With fully custom prompt
        >>> extractor = SchemaExtractor(
        ...     schema=Invoice,
        ...     llm=AnthropicLLM(),
        ...     searcher=BM25Searcher(),
        ...     system_prompt="You are an expert invoice parser...",
        ... )
        >>>
        >>> result = extractor.extract(document)
        >>> print(result.data.total)
    """

    schema: Type[T]
    llm: LLM
    searcher: Searcher | None = None
    retriever: Any = None  # Optional Retriever for semantic search
    top_k: int = 3
    verify: bool = True
    temperature: float = 0.0
    max_tokens: int = 4096

    # Custom prompt options
    system_prompt: str | None = None
    extra_instructions: str | None = None
    prompt_builder: PromptBuilder | None = None

    # Batching options for large schemas
    max_fields_per_batch: int | None = None  # None = all fields in one call
    max_context_chars: int = 100000  # Max chars for contexts per batch
    include_document_text: bool = True  # Include full doc text in prompt
    max_document_chars: int = 50000  # Truncate document text

    # Internal state
    _indexed: bool = field(default=False, init=False, repr=False)

    def extract(self, document: Document) -> ExtractionResult[T]:
        """
        Extract structured data from a document.

        For each field in the schema:
        1. Search for relevant chunks using the field's query and search_type
        2. Build context from retrieved chunks
        3. Extract value using LLM (batched if schema is large)
        4. Optionally verify against source text

        Args:
            document: Document to extract from.

        Returns:
            ExtractionResult with data, evidence, and metrics.
        """
        start_time = time.time()
        flags: list[ExtractionFlag] = []

        # Index document if not already indexed
        if not self._indexed:
            self._index_document(document)

        # Gather context for each field
        field_contexts = self._gather_field_contexts(document)

        # Split fields into batches if needed
        batches = self._create_field_batches(field_contexts)

        # Extract using LLM (one call per batch)
        extracted_data: dict[str, Any] = {}
        total_input_tokens = 0
        total_output_tokens = 0
        llm_calls = 0

        try:
            for batch_fields, batch_contexts in batches:
                batch_prompt = self._build_extraction_prompt(
                    batch_contexts, batch_fields
                )
                batch_data, input_tokens, output_tokens = self._extract_with_llm(
                    batch_prompt, document, batch_fields
                )
                extracted_data.update(batch_data)
                total_input_tokens += input_tokens
                total_output_tokens += output_tokens
                llm_calls += 1
        except Exception as e:
            return self._failed_result(document, str(e), time.time() - start_time)

        # Parse values through field definitions
        parsed_data = {}
        for name, field_def in self.schema.get_fields().items():
            raw_value = extracted_data.get(name)
            if raw_value is not None:
                parsed_data[name] = field_def.parse(raw_value)
            else:
                parsed_data[name] = field_def.default

        # Verify if enabled
        verification_results: list[VerificationResult] = []
        evidence_map: dict[str, Evidence] = {}

        if self.verify:
            verification_results, evidence_map = self._verify_extraction(
                parsed_data, field_contexts, flags
            )

        # Create schema instance
        try:
            data_instance = self.schema(**parsed_data)
        except Exception as e:
            flags.append(
                ExtractionFlag(
                    type=ExtractionFlagType.SCHEMA_ERROR,
                    message=f"Failed to create schema instance: {e}",
                )
            )
            return self._failed_result(document, str(e), time.time() - start_time)

        # Compute status
        status = self._compute_status(verification_results, flags)
        confidence = self._compute_confidence(verification_results)

        # Build stats
        duration_ms = int((time.time() - start_time) * 1000)
        stats = ExtractionStats(
            total_duration_ms=duration_ms,
            extraction_duration_ms=duration_ms,
            extraction_input_tokens=total_input_tokens,
            extraction_output_tokens=total_output_tokens,
            extraction_llm_calls=llm_calls,
            fields_verified=len(verification_results),
            fields_passed=sum(
                1 for vr in verification_results
                if vr.status == VerificationStatus.MATCH
            ),
        )

        return ExtractionResult(
            data=data_instance,
            status=status,
            confidence=confidence,
            document_id=document.id,
            evidence_map=evidence_map,
            verification_results=tuple(verification_results),
            flags=tuple(flags),
            stats=stats,
        )

    def _index_document(self, document: Document) -> None:
        """Index document chunks in searcher(s)."""
        chunks = document.chunks

        if not chunks:
            return

        # Prepare chunk texts and metadata
        texts = [chunk.text for chunk in chunks]
        metadata = [
            {
                "chunk_index": chunk.index,
                "page": chunk.page,
            }
            for chunk in chunks
        ]

        # Index in BM25 searcher
        if self.searcher:
            self.searcher.index(texts, metadata)

        # Index in semantic retriever if available
        if self.retriever and hasattr(self.retriever, "index"):
            self.retriever.index(document)

        self._indexed = True

    def _gather_field_contexts(
        self, document: Document
    ) -> dict[str, list[SearchResult]]:
        """Gather relevant context for each field based on search type."""
        field_contexts: dict[str, list[SearchResult]] = {}

        for name, field_def in self.schema.get_fields().items():
            results: list[SearchResult] = []

            if field_def.search_type == SearchType.BM25:
                if self.searcher:
                    results = self.searcher.search(field_def.query, self.top_k)

            elif field_def.search_type == SearchType.SEMANTIC:
                if self.retriever and hasattr(self.retriever, "search"):
                    retriever_results = self.retriever.search(
                        field_def.query, top_k=self.top_k
                    )
                    results = self._convert_retriever_results(retriever_results)

            elif field_def.search_type == SearchType.HYBRID:
                # Combine BM25 and semantic results
                bm25_results = []
                semantic_results = []

                if self.searcher:
                    bm25_results = self.searcher.search(field_def.query, self.top_k)

                if self.retriever and hasattr(self.retriever, "search"):
                    retriever_results = self.retriever.search(
                        field_def.query, top_k=self.top_k
                    )
                    semantic_results = self._convert_retriever_results(retriever_results)

                results = self._merge_results(bm25_results, semantic_results)

            field_contexts[name] = results

        return field_contexts

    def _convert_retriever_results(self, results: list[Any]) -> list[SearchResult]:
        """Convert retriever results to SearchResult format."""
        search_results = []
        for r in results:
            if hasattr(r, "text"):
                search_results.append(
                    SearchResult(
                        text=r.text,
                        score=getattr(r, "score", 0.0),
                        chunk_index=getattr(r, "chunk_index", 0),
                        page=getattr(r, "page"),
                        metadata=getattr(r, "metadata", {}),
                    )
                )
            elif isinstance(r, dict):
                search_results.append(
                    SearchResult(
                        text=r.get("text", ""),
                        score=r.get("score", 0.0),
                        chunk_index=r.get("chunk_index", 0),
                        page=r.get("page"),
                        metadata=r.get("metadata", {}),
                    )
                )
        return search_results

    def _merge_results(
        self,
        bm25_results: list[SearchResult],
        semantic_results: list[SearchResult],
    ) -> list[SearchResult]:
        """Merge BM25 and semantic results using RRF."""
        # Simple merge for now - dedupe by chunk_index, prefer higher score
        seen: dict[int, SearchResult] = {}

        for r in bm25_results + semantic_results:
            if r.chunk_index not in seen or r.score > seen[r.chunk_index].score:
                seen[r.chunk_index] = r

        # Sort by score
        return sorted(seen.values(), key=lambda x: x.score, reverse=True)[: self.top_k]

    def _create_field_batches(
        self, field_contexts: dict[str, list[SearchResult]]
    ) -> list[tuple[list[str], dict[str, list[SearchResult]]]]:
        """
        Split fields into batches based on context size limits.

        Returns list of (field_names, field_contexts) tuples, one per batch.
        """
        all_fields = list(self.schema.get_fields().keys())

        # If no limits set, return all fields in one batch
        if self.max_fields_per_batch is None and self.max_context_chars >= 1000000:
            return [(all_fields, field_contexts)]

        batches: list[tuple[list[str], dict[str, list[SearchResult]]]] = []
        current_batch: list[str] = []
        current_contexts: dict[str, list[SearchResult]] = {}
        current_chars = 0

        for field_name in all_fields:
            contexts = field_contexts.get(field_name, [])

            # Calculate chars for this field's contexts
            field_chars = sum(len(ctx.text) for ctx in contexts)

            # Check if adding this field would exceed limits
            would_exceed_chars = (current_chars + field_chars) > self.max_context_chars
            would_exceed_fields = (
                self.max_fields_per_batch is not None
                and len(current_batch) >= self.max_fields_per_batch
            )

            # Start new batch if limits exceeded (and current batch not empty)
            if current_batch and (would_exceed_chars or would_exceed_fields):
                batches.append((current_batch, current_contexts))
                current_batch = []
                current_contexts = {}
                current_chars = 0

            # Add field to current batch
            current_batch.append(field_name)
            current_contexts[field_name] = contexts
            current_chars += field_chars

        # Don't forget the last batch
        if current_batch:
            batches.append((current_batch, current_contexts))

        return batches

    def _build_extraction_prompt(
        self,
        field_contexts: dict[str, list[SearchResult]],
        field_names: list[str] | None = None,
    ) -> str:
        """Build extraction prompt with field-specific context.

        Args:
            field_contexts: Retrieved contexts for each field.
            field_names: Subset of fields to include (None = all fields).

        Uses custom prompts if configured:
        1. If prompt_builder is set, calls it with (schema, field_contexts)
        2. If system_prompt is set, uses it directly
        3. Otherwise builds default prompt with extra_instructions appended
        """
        # Option 1: Custom prompt builder function
        if self.prompt_builder is not None:
            return self.prompt_builder(self.schema, field_contexts)

        # Option 2: Fully custom system prompt
        if self.system_prompt is not None:
            return self.system_prompt

        # Determine which fields to include
        all_fields = self.schema.get_fields()
        if field_names is not None:
            fields_to_include = {k: all_fields[k] for k in field_names if k in all_fields}
        else:
            fields_to_include = all_fields

        # Option 3: Default prompt with optional extra instructions
        lines = [
            "Extract the following fields from the document.",
            "For each field, relevant excerpts from the document are provided.",
            "",
        ]

        for name, field_def in fields_to_include.items():
            lines.append(f"## {field_def.label or name}")

            if field_def.description:
                lines.append(f"Description: {field_def.description}")

            lines.append(f"Required: {'Yes' if field_def.required else 'No'}")

            # Add context excerpts
            contexts = field_contexts.get(name, [])
            if contexts:
                lines.append("Relevant excerpts:")
                for i, ctx in enumerate(contexts, 1):
                    lines.append(f"  [{i}] {ctx.text[:500]}...")
            else:
                lines.append("(No specific excerpts found - extract from full document)")

            lines.append("")

        lines.append(
            "Return the extracted values as JSON matching the schema. "
            "Use null for values not found in the document."
        )

        # Append extra instructions if provided
        if self.extra_instructions:
            lines.append("")
            lines.append("ADDITIONAL INSTRUCTIONS:")
            lines.append(self.extra_instructions)

        return "\n".join(lines)

    def _extract_with_llm(
        self,
        prompt: str,
        document: Document,
        field_names: list[str] | None = None,
    ) -> tuple[dict[str, Any], int, int]:
        """Extract using LLM with structured output.

        Args:
            prompt: System prompt for extraction.
            document: Document to extract from.
            field_names: Subset of fields to extract (None = all fields).
        """
        # Build schema for specified fields only
        if field_names is not None:
            all_fields = self.schema.get_fields()
            properties = {}
            required = []
            for name in field_names:
                if name in all_fields:
                    field_def = all_fields[name]
                    prop_schema = field_def.to_json_schema()
                    if field_def.description:
                        prop_schema["description"] = field_def.description
                    properties[name] = prop_schema
                    if field_def.required:
                        required.append(name)
            schema_json = {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        else:
            schema_json = self.schema.to_json_schema()

        # Build user message with document text
        doc_text = document.text
        if self.include_document_text:
            doc_text = doc_text[: self.max_document_chars]
            user_content = f"Document:\n\n{doc_text}"
        else:
            user_content = "Extract from the excerpts provided above."

        messages = [
            Message(role=Role.SYSTEM, content=prompt),
            Message(role=Role.USER, content=user_content),
        ]

        # Use tool calling for structured output
        tool = Tool(
            name="extract_data",
            description="Extract structured data from the document",
            parameters=schema_json,
        )

        response = self.llm.complete(
            messages=messages,
            tools=[tool],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        # Parse tool call response
        if response.tool_calls:
            return (
                response.tool_calls[0].arguments,
                response.input_tokens,
                response.output_tokens,
            )

        # If no tool call, try to parse content as JSON
        import json

        try:
            data = json.loads(response.content or "{}")
            return data, response.input_tokens, response.output_tokens
        except json.JSONDecodeError:
            return {}, response.input_tokens, response.output_tokens

    def _verify_extraction(
        self,
        data: dict[str, Any],
        field_contexts: dict[str, list[SearchResult]],
        flags: list[ExtractionFlag],
    ) -> tuple[list[VerificationResult], dict[str, Evidence]]:
        """Verify extracted values against source text."""
        results: list[VerificationResult] = []
        evidence_map: dict[str, Evidence] = {}

        for name, field_def in self.schema.get_fields().items():
            extracted_value = data.get(name)
            contexts = field_contexts.get(name, [])

            # Skip verification if no value or no context
            if extracted_value is None:
                if field_def.required:
                    results.append(
                        VerificationResult(
                            path=name,
                            status=VerificationStatus.NOT_FOUND,
                            extracted_value=None,
                        )
                    )
                    flags.append(
                        ExtractionFlag(
                            type=ExtractionFlagType.NOT_FOUND,
                            message=f"Required field not found: {name}",
                            path=name,
                        )
                    )
                continue

            if not contexts:
                # No context to verify against
                results.append(
                    VerificationResult(
                        path=name,
                        status=VerificationStatus.SKIPPED,
                        extracted_value=extracted_value,
                    )
                )
                continue

            # Try to find matching value in context
            candidates: list[EvidenceCandidate] = []

            for ctx in contexts:
                # Parse value from context text
                found_value = field_def.parse_from_text(ctx.text)

                if found_value is not None:
                    candidates.append(
                        EvidenceCandidate(
                            quote=ctx.text[:500],
                            chunk_index=ctx.chunk_index,
                            score=ctx.score,
                            page=ctx.page,
                            parsed_value=found_value,
                        )
                    )

            # Check if any candidate matches
            matching_candidate = None
            for candidate in candidates:
                if field_def.compare(extracted_value, candidate.parsed_value):
                    matching_candidate = candidate
                    break

            if matching_candidate:
                evidence = Evidence(
                    value=extracted_value,
                    quote=matching_candidate.quote,
                    page=matching_candidate.page,
                    bbox=matching_candidate.bbox,
                    chunk_index=matching_candidate.chunk_index,
                    confidence=min(1.0, matching_candidate.score),
                    verified=True,
                )
                evidence_map[name] = evidence

                results.append(
                    VerificationResult(
                        path=name,
                        status=VerificationStatus.MATCH,
                        extracted_value=extracted_value,
                        found_value=matching_candidate.parsed_value,
                        evidence=evidence,
                        candidates=tuple(candidates),
                    )
                )
            elif candidates:
                # Found candidates but no match - mismatch
                best = candidates[0]
                evidence = Evidence(
                    value=best.parsed_value,
                    quote=best.quote,
                    page=best.page,
                    bbox=best.bbox,
                    chunk_index=best.chunk_index,
                    confidence=min(1.0, best.score),
                    verified=False,
                )

                results.append(
                    VerificationResult(
                        path=name,
                        status=VerificationStatus.MISMATCH,
                        extracted_value=extracted_value,
                        found_value=best.parsed_value,
                        evidence=evidence,
                        candidates=tuple(candidates),
                    )
                )

                flags.append(
                    ExtractionFlag(
                        type=ExtractionFlagType.MISMATCH,
                        message=f"Extracted {extracted_value}, found {best.parsed_value}",
                        path=name,
                    )
                )
            else:
                # No candidates found
                results.append(
                    VerificationResult(
                        path=name,
                        status=VerificationStatus.NOT_FOUND,
                        extracted_value=extracted_value,
                    )
                )

        return results, evidence_map

    def _compute_status(
        self,
        results: list[VerificationResult],
        flags: list[ExtractionFlag],
    ) -> ExtractionStatus:
        """Compute extraction status from verification results."""
        if not results:
            return ExtractionStatus.VERIFIED

        matches = sum(1 for r in results if r.status == VerificationStatus.MATCH)
        failures = sum(1 for r in results if r.is_failure)

        if failures == 0:
            return ExtractionStatus.VERIFIED
        elif matches > 0:
            return ExtractionStatus.PARTIAL
        else:
            return ExtractionStatus.FAILED

    def _compute_confidence(self, results: list[VerificationResult]) -> float:
        """Compute overall confidence from verification results."""
        if not results:
            return 1.0

        confidences = []
        for r in results:
            if r.evidence:
                confidences.append(r.evidence.confidence)
            elif r.status == VerificationStatus.MATCH:
                confidences.append(1.0)
            elif r.status == VerificationStatus.SKIPPED:
                confidences.append(0.5)
            else:
                confidences.append(0.0)

        return sum(confidences) / len(confidences) if confidences else 0.0

    def _failed_result(
        self, document: Document, error: str, elapsed: float
    ) -> ExtractionResult[T]:
        """Create a failed extraction result."""
        return ExtractionResult(
            data=None,  # type: ignore
            status=ExtractionStatus.FAILED,
            confidence=0.0,
            document_id=document.id,
            evidence_map={},
            verification_results=(),
            flags=(
                ExtractionFlag(
                    type=ExtractionFlagType.TOOL_ERROR,
                    message=f"Extraction failed: {error}",
                ),
            ),
            stats=ExtractionStats(total_duration_ms=int(elapsed * 1000)),
        )


__all__ = ["SchemaExtractor"]
