# Pullcite

**Evidence-backed structured extraction from documents.**

Pullcite extracts structured data from documents using LLMs while providing **proof of where each value came from** in the source (quote + page + bounding box).

Define Django-style schemas where each field specifies its own search query. Pullcite searches the document per-field, providing relevant context to the LLM, then verifies extracted values against the source.

---

## Installation

```bash
# Core package
pip install pullcite

# With providers
pip install pullcite[anthropic]      # Anthropic Claude
pip install pullcite[openai]         # OpenAI GPT
pip install pullcite[tantivy]        # High-performance BM25 search
pip install pullcite[voyage]         # Voyage AI embeddings (for semantic search)
pip install pullcite[docling]        # PDF/DOCX parsing with coordinates

# Everything
pip install pullcite[all]
```

---

## Quick Start

```python
from pullcite import (
    Document,
    ExtractionSchema,
    Extractor,
    DecimalField,
    StringField,
    SearchType,
    BM25Searcher,
)
from pullcite.llms.anthropic import AnthropicLLM

# 1. Define your schema with field-level search queries
class Invoice(ExtractionSchema):
    vendor = StringField(
        query="vendor company name supplier",
        search_type=SearchType.BM25,
        description="Company that issued the invoice",
    )
    total = DecimalField(
        query="total amount due grand total",
        search_type=SearchType.BM25,
        description="Total amount due",
    )

# 2. Create extractor
extractor = Extractor(
    schema=Invoice,
    llm=AnthropicLLM(),
    searcher=BM25Searcher(),
)

# 3. Extract with evidence
doc = Document.from_file("invoice.pdf")
result = extractor.extract(doc)

# 4. Access data and evidence
print(result.data.total)         # Decimal("1500.00")
print(result.data.vendor)        # "Acme Corp"
print(result.status)             # ExtractionStatus.VERIFIED

evidence = result.evidence_map["total"]
print(evidence.quote)            # "Grand Total: $1,500.00"
print(evidence.page)             # 1
print(evidence.bbox)             # (72.0, 540.2, 200.5, 555.8)
```

---

## Health Insurance Example

```python
from decimal import Decimal
from pullcite import (
    Document,
    ExtractionSchema,
    Extractor,
    StringField,
    DecimalField,
    PercentField,
    BooleanField,
    SearchType,
    BM25Searcher,
)
from pullcite.llms.anthropic import AnthropicLLM


class HealthPlan(ExtractionSchema):
    """Health insurance plan extraction schema."""

    plan_name = StringField(
        query="plan name health plan title",
        search_type=SearchType.BM25,
    )
    plan_type = StringField(
        query="plan type HMO PPO EPO",
        search_type=SearchType.BM25,
    )

    # Deductibles
    individual_deductible = DecimalField(
        query="individual deductible annual",
        search_type=SearchType.BM25,
    )
    family_deductible = DecimalField(
        query="family deductible annual",
        search_type=SearchType.BM25,
    )

    # Out-of-pocket
    individual_oop_max = DecimalField(
        query="individual out-of-pocket maximum",
        search_type=SearchType.BM25,
    )
    family_oop_max = DecimalField(
        query="family out-of-pocket maximum",
        search_type=SearchType.BM25,
    )

    # Copays
    pcp_copay = DecimalField(
        query="primary care physician copay PCP",
        search_type=SearchType.BM25,
    )
    specialist_copay = DecimalField(
        query="specialist copay",
        search_type=SearchType.BM25,
    )
    er_copay = DecimalField(
        query="emergency room ER copay",
        search_type=SearchType.BM25,
    )

    # Coinsurance
    coinsurance = PercentField(
        query="coinsurance percentage member pays",
        search_type=SearchType.BM25,
    )

    # Prescriptions
    generic_rx = DecimalField(
        query="generic prescription drug copay tier 1",
        search_type=SearchType.BM25,
        required=False,
    )

    # Coverage
    preventive_covered = BooleanField(
        query="preventive care covered no cost",
        search_type=SearchType.BM25,
        required=False,
    )


# Create extractor with custom instructions
extractor = Extractor(
    schema=HealthPlan,
    llm=AnthropicLLM(model="claude-sonnet-4-20250514"),
    searcher=BM25Searcher(),
    extra_instructions="""
    - Extract IN-NETWORK values when both in/out-of-network are shown
    - Coinsurance is what the MEMBER pays, not the plan
    - "No charge" or "Covered in full" means $0
    """,
)

# Extract
doc = Document.from_file("summary_of_benefits.pdf")
result = extractor.extract(doc)

# Print results
print(f"Plan: {result.data.plan_name} ({result.data.plan_type})")
print(f"Individual Deductible: ${result.data.individual_deductible}")
print(f"PCP Copay: ${result.data.pcp_copay}")
print(f"Coinsurance: {result.data.coinsurance}%")
print(f"Status: {result.status}")
```

---

## Field Types

| Field Type | Python Type | Parses | Example |
|------------|-------------|--------|---------|
| `StringField` | `str` | Text | `"Acme Corp"` |
| `IntegerField` | `int` | Integers | `100`, `"100 days"` |
| `FloatField` | `float` | Decimals | `3.14` |
| `DecimalField` | `Decimal` | Currency | `"$1,500.00"` → `Decimal("1500.00")` |
| `CurrencyField` | `Decimal` | Currency | Same as Decimal, with symbol handling |
| `PercentField` | `float` | Percentages | `"30%"`, `0.30` → `30.0` |
| `BooleanField` | `bool` | Yes/No | `"yes"`, `"true"`, `1` → `True` |
| `DateField` | `str` | Dates | `"2024-01-15"` |
| `ListField` | `list` | Arrays | `["a", "b", "c"]` |
| `EnumField` | `str` | Choices | Must be one of defined choices |

---

## Search Types

Each field specifies how to search for evidence:

```python
class Document(ExtractionSchema):
    # BM25: Keyword search (fast, no embeddings needed)
    invoice_number = StringField(
        query="invoice number invoice #",
        search_type=SearchType.BM25,
    )

    # Semantic: Vector similarity (requires embeddings)
    description = StringField(
        query="product service description",
        search_type=SearchType.SEMANTIC,
    )

    # Hybrid: Combined BM25 + semantic with rank fusion
    vendor = StringField(
        query="vendor company supplier",
        search_type=SearchType.HYBRID,
    )
```

For semantic/hybrid search, provide a retriever:

```python
from pullcite.embeddings.openai import OpenAIEmbedder
from pullcite.retrieval.memory import MemoryRetriever

extractor = Extractor(
    schema=MySchema,
    llm=my_llm,
    searcher=BM25Searcher(),
    retriever=MemoryRetriever(OpenAIEmbedder()),  # For semantic fields
)
```

---

## Custom Prompts

### Extra Instructions (append to default prompt)

```python
extractor = Extractor(
    schema=Invoice,
    llm=my_llm,
    searcher=BM25Searcher(),
    extra_instructions="""
    - All amounts are in USD
    - Dates should be YYYY-MM-DD format
    - Use the value from "Grand Total", not subtotals
    """,
)
```

### Full System Prompt (replace default)

```python
extractor = Extractor(
    schema=Invoice,
    llm=my_llm,
    searcher=BM25Searcher(),
    system_prompt="""You are an expert invoice parser.
    Extract all fields precisely. Be careful with:
    - Currency formatting
    - Tax calculations
    - Line item totals vs grand total
    """,
)
```

### Custom Prompt Builder (full control)

```python
def my_prompt_builder(schema, field_contexts):
    """Build custom prompt with access to schema and retrieved contexts."""
    lines = ["Extract these fields:"]
    for name, field in schema.get_fields().items():
        contexts = field_contexts.get(name, [])
        lines.append(f"\n## {name}")
        if contexts:
            lines.append(f"Found in: {contexts[0].text[:200]}")
    return "\n".join(lines)

extractor = Extractor(
    schema=Invoice,
    llm=my_llm,
    searcher=BM25Searcher(),
    prompt_builder=my_prompt_builder,
)
```

---

## Handling Large Documents

For documents that exceed context limits, use batching:

```python
extractor = Extractor(
    schema=LargeSchema,  # 50+ fields
    llm=my_llm,
    searcher=BM25Searcher(),

    # Batching options
    max_fields_per_batch=10,       # Max fields per LLM call
    max_context_chars=50000,       # Max context chars per batch

    # Skip full document text (use only retrieved excerpts)
    include_document_text=False,
    top_k=10,                      # More chunks per field
)
```

This splits extraction into multiple LLM calls, each handling a subset of fields with their relevant context.

---

## Evidence

Every extracted value can be traced to the source:

```python
result = extractor.extract(document)

for field_name, evidence in result.evidence_map.items():
    print(f"{field_name}:")
    print(f"  Value: {evidence.value}")
    print(f"  Quote: {evidence.quote}")
    print(f"  Page: {evidence.page}")
    print(f"  Bounding Box: {evidence.bbox}")  # (x0, y0, x1, y1) in PDF points
    print(f"  Confidence: {evidence.confidence:.0%}")
    print(f"  Verified: {evidence.verified}")
```

---

## Verification Status

```python
from pullcite import ExtractionStatus

result = extractor.extract(document)

if result.status == ExtractionStatus.VERIFIED:
    print("All fields verified against source")
elif result.status == ExtractionStatus.PARTIAL:
    print("Some fields could not be verified")
elif result.status == ExtractionStatus.FAILED:
    print("Extraction failed")

# Check individual field results
for vr in result.verification_results:
    print(f"{vr.path}: {vr.status.value}")
```

---

## LLM Providers

### Anthropic Claude

```python
from pullcite.llms.anthropic import AnthropicLLM

llm = AnthropicLLM(
    api_key="...",  # Or ANTHROPIC_API_KEY env var
    model="claude-sonnet-4-20250514",
)
```

### OpenAI GPT

```python
from pullcite.llms.openai import OpenAILLM

llm = OpenAILLM(
    api_key="...",  # Or OPENAI_API_KEY env var
    model="gpt-4o",
)
```

---

## Project Structure

```
pullcite/
├── __init__.py          # Main exports
├── core/
│   ├── document.py      # Document loading + chunking
│   ├── chunk.py         # Chunk dataclass
│   ├── evidence.py      # Evidence, VerificationResult
│   └── result.py        # ExtractionResult, stats
├── schema/
│   ├── base.py          # ExtractionSchema, Field, SearchType
│   ├── fields.py        # StringField, DecimalField, etc.
│   └── extractor.py     # SchemaExtractor (Extractor)
├── search/
│   ├── base.py          # Searcher ABC, SearchResult
│   ├── bm25.py          # BM25Searcher (tantivy)
│   └── hybrid.py        # HybridSearcher
├── embeddings/
│   ├── openai.py        # OpenAI embeddings
│   ├── voyage.py        # Voyage AI embeddings
│   └── local.py         # Sentence Transformers
├── retrieval/
│   ├── memory.py        # In-memory vector store
│   ├── chroma.py        # ChromaDB
│   └── pgvector.py      # PostgreSQL pgvector
└── llms/
    ├── anthropic.py     # Anthropic Claude
    └── openai.py        # OpenAI GPT
```

---

## Environment Variables

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export VOYAGE_API_KEY="..."
```

---

## Development

```bash
git clone https://github.com/usercando/pullcite
cd pullcite
pip install -e ".[dev]"

pytest tests/ -v
```

---

## License

MIT
