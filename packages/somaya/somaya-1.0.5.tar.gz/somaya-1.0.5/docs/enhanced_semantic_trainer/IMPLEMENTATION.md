# Implementation Details

## Architecture

```
EnhancedSOMASemanticTrainer
├── Base embeddings (token_embeddings, context_embeddings)
├── Multi-stream embeddings (one per stream)
├── Temporal embeddings (position-dependent)
├── Sequential embeddings (Token[t] → Token[t+1])
├── Content-ID clusters
├── Deterministic UID graph
└── Cross-stream alignment matrices
```

## Training Process

1. **Build Vocabulary**
   - Collect tokens from all streams
   - Filter by min_count
   - Store metadata (content_id, frontend, backend, etc.)

2. **Build Content-ID Clusters**
   - Group tokens by content_id
   - Create cluster mappings

3. **Initialize Deterministic Graph**
   - Build UID-based relationships
   - Store neighbor connections

4. **Build Co-occurrence**
   - Immediate neighbors (prev_uid, next_uid) - weight 2.0
   - Context window - weight 1.0/distance
   - Content-ID clusters - weight 0.5
   - Sequential flow - weight 1.5

5. **Train Embeddings**
   - Skip-gram style learning
   - Positive samples (co-occurring tokens)
   - Negative sampling (random non-co-occurring)
   - Update all embedding types

## Embedding Generation

When getting an embedding for a token:

1. **Base embedding** (token_embeddings[idx])
2. **+ Temporal component** (if position provided) - 0.1 weight
3. **+ Stream component** (if stream provided) - 0.1 weight
4. **+ Math properties** (if enabled) - 0.05 weight
5. **Normalize** (L2 normalization)

## Feature Flags

All features can be enabled/disabled:

```python
trainer = EnhancedSOMASemanticTrainer(
    use_multi_stream=True,           # Multi-stream embeddings
    use_temporal=True,                # Position-dependent
    use_content_id_clustering=True,   # Content-ID clustering
    use_math_properties=True,        # Math properties
    use_cross_stream_alignment=True,   # Cross-stream alignment
    use_deterministic_graph=True      # UID graph
)
```

## Memory Usage

- Base embeddings: vocab_size × embedding_dim × 2 (token + context)
- Multi-stream: vocab_size × embedding_dim × num_streams
- Temporal: max_position × embedding_dim
- Sequential: vocab_size × embedding_dim
- Total: ~(vocab_size × embedding_dim × (2 + num_streams + 1) + max_position × embedding_dim)

For vocab_size=50k, embedding_dim=768, num_streams=9:
- ~50k × 768 × 12 = ~460MB (float32)

## Performance Tips

1. **Limit vocabulary size** - Use max_vocab_size parameter
2. **Sample co-occurrence pairs** - Already implemented (max 100k pairs)
3. **Reduce epochs** - Start with 5-10 epochs
4. **Disable unused features** - Turn off features you don't need
5. **Use sparse representation** - For very large vocabularies

## Future Enhancements

Potential additions:
- Source-aware semantics (different spaces for different sources)
- Document structure awareness (sentence/paragraph boundaries)
- Hierarchical learning (char → subword → word)
- Better negative sampling (content-ID based)
- Learning rate scheduling

