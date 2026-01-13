# Detailed Workflow: Weaviate-First Storage Strategy

## Complete Step-by-Step Execution Flow

### PHASE 1: INITIALIZATION (Lines 2415-2459)
```
1. Check dependencies (wikipedia, numpy, faiss-cpu)
2. Ask user for embedding strategy (feature_based vs hybrid)
3. Initialize UnifiedVectorStoreExample
4. Initialize vector stores:
   - Weaviate (cloud-based)
   - FAISS (in-memory)
   - ChromaDB (persistent disk)
5. Show feature selection menu (user chooses which features to run)
```

### PHASE 2: DATA PREPARATION (Lines 2693-2746)

#### Scenario A: New Data (not loading from disk)
```
IF 'e' in features_to_run:
    → Step 1: retrieval_before_processing("machine learning", top_k=5)
       - Check Weaviate/FAISS/ChromaDB for similar tokens BEFORE processing
       - Demonstrates context memory

IF 'b' in features_to_run:
    → Step 1.5: show_detailed_embeddings("Hello world, this is SOMA!")
       - Display token-by-token embedding details
       - Shows UID, Frontend, Content ID, Prev/Next UID

IF 'a' in features_to_run OR 'c' in features_to_run:
    → Step 2: tokenize_text(text)
       - Break text into tokens using SOMA
       - Store in self.tokens
    
    → Step 3: generate_embeddings(strategy="feature_based")
       - Generate 768-dim embeddings for all tokens
       - Store in self.embeddings
    
    → Step 4: store_tokens_weaviate_first()  ⭐ PRIORITY STORAGE
       - Generate unique run_id, session_id, date tags
       - Prepare metadata for each token
       - Store ALL tokens + embeddings in Weaviate IMMEDIATELY
       - This ensures data is safe in cloud before any other operations
```

#### Scenario B: Loading from Disk
```
IF tokens.pkl exists:
    → Ask user: "Resume? (y/n)"
    IF yes:
        → Load tokens from disk
        → Load embedding batches (if available)
        → Load into vector stores (Weaviate, FAISS, ChromaDB)
        
        IF embeddings missing:
            → Generate embeddings for loaded tokens
            → Ask: "Store tokens in Weaviate? (y/n)"
            IF yes:
                → store_tokens_weaviate_first()  ⭐ PRIORITY STORAGE
```

### PHASE 3: SEARCH & RETRIEVAL OPERATIONS (Lines 2748-2794)

**These operations run AFTER Weaviate storage is complete:**

```
IF 'd' in features_to_run:
    → semantic_search("machine", top_k=10, store_name="all")
    → semantic_search("learning", top_k=10, store_name="all")
    - Search across Weaviate, FAISS, ChromaDB
    - Filter stop words
    - Apply similarity thresholds

IF 'f' in features_to_run:
    → query_by_id(token_id, store_name="weaviate")
    - Retrieve specific token by UUID from Weaviate
    - Demonstrates direct ID lookup
```

### PHASE 4: ANALYSIS & COMPARISON OPERATIONS (Lines 2753-2786)

```
IF 'g' in features_to_run:
    → compare_stores("artificial", top_k=10)
    - Compare search results between Weaviate, FAISS, ChromaDB
    - Calculate overlap percentages

IF 'h' in features_to_run:
    → find_related_concepts(["machine", "learning"], top_k=15)
    - Average embeddings of multiple tokens
    - Find semantically related concepts

IF 'i' in features_to_run:
    → compare_tokens("artificial", "intelligence")
    → compare_tokens("machine", "learning")
    - Direct token-to-token similarity comparison
    - Cosine similarity calculation

IF 'j' in features_to_run:
    → find_concept_cluster("neural", cluster_size=10)
    - Find cluster of related concepts around seed token

IF 'k' in features_to_run:
    → explore_concept("neural", depth=2, top_k_per_level=10)
    - Multi-level concept exploration
    - Breadth-first search through semantic relationships
```

### PHASE 5: EMBEDDING & DOCUMENT OPERATIONS (Lines 2769-2786)

```
IF 'l' in features_to_run:
    → compare_embeddings("machine learning", "artificial intelligence")
    → compare_embeddings("natural language processing", "deep learning")
    - Text-to-text cosine similarity
    - Generate embeddings for both texts and compare

IF 'm' in features_to_run:
    → get_document_embeddings(documents, method="mean")
    - Generate document-level embeddings (mean/max/sum)
    - Compute inter-document similarities
```

### PHASE 6: EVALUATION & QUALITY OPERATIONS (Lines 2781-2786)

```
IF 'n' in features_to_run:
    → evaluate_quality(probes, top_k=10)
    - Evaluate embedding quality using probe tokens
    - Test semantic search accuracy

IF 'o' in features_to_run:
    → analyze_clusters(sample_size=100, top_k=5)
    - Analyze token clusters
    - Find groups of similar tokens
```

### PHASE 7: ADVANCED FEATURES (Lines 2796-2856)

```
IF 's' in features_to_run:
    → visualize_embeddings(limit=100)
    - t-SNE dimensionality reduction
    - Create 2D visualization of embedding space
    - Save as PNG file

IF 'r' in features_to_run:
    → build_context_fusion_embeddings(
         context_window=5,
         use_positional=True,
         use_neighbor_attention=True,
         use_content_grouping=True,
         min_similarity_threshold=0.3
       )
    - Build context-aware embeddings using SOMA's native mechanisms
    - Uses prev_uid/next_uid, content_id, global_id
    - Then test with search_with_context_fusion()

IF 'p' in features_to_run:
    → evaluate_semantic_alignment()
    - Test how well SOMA embeddings match human semantic judgments
    - Calculate mean error, correlation
    
    IF 'q' in features_to_run AND mean_error > 0.2:
        → train_embedding_alignment(training_pairs, epochs=20)
        - Train alignment using labeled pairs
        - Multi-loss: contrastive + MSE
        - Save alignment model to disk

IF 't' in features_to_run:
    → interactive_search()
    - Interactive command-line interface
    - Commands: search, compare, related, cluster, explore
    - Runs until user types 'quit' or 'exit'
```

### PHASE 8: FINAL STORAGE (Lines 2861-2868) ⭐ END OF WORKFLOW

```
IF 'c' in features_to_run AND (FAISS exists OR ChromaDB exists):
    → store_tokens_other_stores()
    
    This happens AT THE VERY END, after ALL other operations:
    
    1. Store in FAISS:
       - Try to add all tokens + embeddings
       - IF MemoryError: Skip FAISS (already have data in Weaviate)
       - IF other error: Log warning and continue
    
    2. Store in ChromaDB:
       - Chunk data into batches of 5000 tokens
       - Store each chunk sequentially
       - IF compaction error: Skip ChromaDB (already have data in Weaviate)
       - IF other error: Log warning and continue
    
    WHY AT THE END?
    - Weaviate already has everything (stored in Phase 2)
    - If FAISS/ChromaDB fail, no data is lost
    - All analysis/search operations already completed
    - This is just "bonus" storage for faster local search
```

## Key Benefits of This Workflow

1. **Data Safety First**: Weaviate (cloud) gets data immediately → no risk of data loss
2. **No Time Wasting**: Operations continue even if FAISS/ChromaDB fail later
3. **Graceful Degradation**: If local stores fail, Weaviate still has everything
4. **Efficient**: All analysis/search uses Weaviate data (already stored)
5. **Resilient**: Final storage is optional - failures don't break the workflow

## Execution Timeline Example

```
Time 0:00 - Initialize stores
Time 0:05 - Tokenize text (1000 tokens)
Time 0:10 - Generate embeddings
Time 0:15 - ✅ STORE IN WEAVIATE (PRIORITY - DATA IS SAFE)
Time 0:20 - Run semantic search (uses Weaviate)
Time 0:25 - Run concept exploration (uses Weaviate)
Time 0:30 - Run quality evaluation (uses Weaviate)
Time 0:35 - Run context fusion (uses Weaviate)
Time 0:40 - Run visualization
Time 0:45 - Interactive search mode
Time 0:50 - ⏰ FINAL: Try to store in FAISS/ChromaDB
           (If fails, no problem - Weaviate has everything)
Time 0:55 - Complete!
```

## Code Locations

- **Weaviate Storage**: `store_tokens_weaviate_first()` - Line 897
- **Other Stores Storage**: `store_tokens_other_stores()` - Line 946
- **Main Workflow**: `main()` function - Line 2415
- **Priority Storage Call**: Line 2720 (new data) or 2738 (loaded data)
- **Final Storage Call**: Line 2868 (end of all operations)

