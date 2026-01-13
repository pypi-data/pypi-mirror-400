# SOMA Source Map System

Universal knowledge source registration and tagging system for SOMA, designed for Railway compute.

## Overview

The SOMA Source Map system provides:

1. **Source UID Generation**: Deterministic 64-bit hash-based UIDs for all knowledge sources
2. **Token Source Tagging**: Every token embeds `{source_id, algorithm_id, timestamp}` metadata
3. **Weighted Embedding Merging**: Combine embeddings from different sources with weighted averaging
4. **Hierarchical Profiling**: Track embedding performance per-source (Wikipedia vs GitHub vs PubMed)

## Quick Start

```python
from src.soma_sources import get_source_map

# Get source map instance
source_map = get_source_map()

# Get source ID for Wikipedia
wikipedia_id = source_map.get_source_id("wikipedia")

# Tag tokens with source metadata
source_tags = source_map.get_source_tags_for_token(
    source_tag="wikipedia",
    algorithm_id="word_tokenization"
)

# Merge embeddings from multiple sources
merged_embedding, combined_metadata = source_map.merge_embeddings([
    (embedding1, tags1),
    (embedding2, tags2),
    (embedding3, tags3)
])
```

## Supported Sources

### Core Knowledge Bases
- `wikipedia` - General human knowledge
- `wikidata` - Structured knowledge graph
- `arxiv` - Scientific papers
- `pubmed` - Biomedical literature
- `project_gutenberg` - Classic literature
- `stackexchange` - QA-style corpora
- `reddit` - Conversational embeddings
- `commoncrawl` - General web data

### Technical Corpora
- `huggingface_datasets` - Prebuilt NLP datasets
- `github_corpus` - Public source code
- `paperswithcode` - ML and AI papers
- `openai_cookbook` - Engineering workflows
- `pytorch_docs` - Framework documentation
- `tensorflow_docs` - TensorFlow documentation

### Domain-Specific
- `financial_reports` - Finance domain
- `legal_cases` - Law domain
- `medical_guidelines` - Medicine domain
- `news_articles` - Journalism domain
- `academic_theses` - Research domain

### Symbolic Data
- `unicode_tables` - Unicode + byte data
- `ascii_map` - Base reference map
- `latex_corpus` - Math and equations
- `json_schema` - Structural boundaries
- `yaml_configs` - Hierarchical structures
- `regex_dataset` - Pattern data

### Cross-Modal
- `wikimedia_images` - Images with text
- `laion_5b` - Large text-image corpus
- `ocr_corpus` - Scanned document text

### Reinforcement
- `user_feedback` - Human-in-the-loop ratings
- `model_logs` - Token/embedding traces
- `synthetic_corpus` - Generated training text

## Railway Compute Integration

The source map system is designed to work seamlessly with Railway compute:

1. **Persistent Registry**: Source registry is saved to `data/soma_sources_registry.json`
2. **Cloud-Friendly**: No local file dependencies, works with Railway's filesystem
3. **Deterministic UIDs**: Same source always generates same UID (important for distributed systems)
4. **Lightweight**: Minimal dependencies, fast initialization

## Usage Examples

See `examples/test_soma_source_map.py` for complete examples.

## API Reference

### `get_source_map(registry_file=None) -> SOMASourceMap`

Get or create the global source map instance.

### `source_map.get_source_id(tag: str) -> Optional[str]`

Get the source UID for a given tag.

### `source_map.get_source_tags_for_token(source_tag, algorithm_id, timestamp) -> Dict`

Generate source tagging metadata for a token.

### `source_map.merge_embeddings(embeddings) -> Tuple[List[float], Dict]`

Merge embeddings from different sources using weighted averaging.

### `source_map.get_performance_profile(category=None) -> Dict`

Get hierarchical performance profile of sources.

