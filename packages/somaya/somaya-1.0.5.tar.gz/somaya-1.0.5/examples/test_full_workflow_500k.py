"""
Full Workflow Test: Tokenization -> Embedding -> Semantic -> Model Outcome
================================================================================

This script tests the complete SOMA workflow with 500k tokens:
1. Tokenization (SOMA)
2. Embedding Generation
3. Semantic Training/Inference
4. Model Outcome (similarity search, clustering, etc.)

You can use:
- Downloaded text (Wikipedia, books, etc.)
- Generated synthetic text
- Your own text file
"""

import sys
import os
import json
import pickle
import gc
import subprocess
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.embeddings.embedding_generator import somaEmbeddingGenerator
from src.embeddings.semantic_trainer import somaSemanticTrainer
from src.embeddings.vector_store import ChromaVectorStore, FAISSVectorStore
from src.core.core_tokenizer import TextTokenizer, all_tokenizations


def check_and_install_dependencies():
    """Check and install required dependencies."""
    print("=" * 80)
    print("CHECKING DEPENDENCIES")
    print("=" * 80)
    
    required_packages = {
        'wikipedia': 'wikipedia',
        'numpy': 'numpy',
        'faiss': 'faiss-cpu',  # or faiss-gpu if you have GPU
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"[OK] {package_name} is installed")
        except ImportError:
            print(f"[ERROR] {package_name} is NOT installed")
            missing.append(package_name)
    
    if missing:
        print(f"\n📦 Installing missing packages: {', '.join(missing)}")
        for package in missing:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"[OK] Installed {package}")
            except subprocess.CalledProcessError:
                print(f"[ERROR] Failed to install {package}. Please install manually: pip install {package}")
                return False
    
    print("\n[OK] All dependencies are ready!")
    return True


def download_wikipedia_sample(num_articles=50):
    """
    Download sample Wikipedia articles.
    Note: This is a simplified version. For production, use the Wikipedia API.
    """
    print("📥 Downloading Wikipedia sample...")
    print("   (For real use, install: pip install wikipedia-api)")
    
    try:
        import wikipedia
        wikipedia.set_lang("en")
        
        articles = []
        topics = [
            "Artificial Intelligence", "Machine Learning", "Natural Language Processing",
            "Deep Learning", "Neural Networks", "Computer Science", "Python Programming",
            "Data Science", "Big Data", "Cloud Computing", "Software Engineering",
            "Web Development", "Mobile Applications", "Database Systems", "Operating Systems",
            "Computer Networks", "Cybersecurity", "Blockchain", "Cryptocurrency", "Quantum Computing",
            "Robotics", "Internet of Things", "Augmented Reality", "Virtual Reality", "Gaming",
            "Social Media", "E-commerce", "Digital Marketing", "Content Management", "User Experience",
            "Graphic Design", "Video Games", "Music Production", "Film Industry", "Photography",
            "Travel", "Cooking", "Fitness", "Health", "Education", "History", "Geography",
            "Mathematics", "Physics", "Chemistry", "Biology", "Medicine", "Psychology", "Philosophy",
            "Literature", "Art"
        ]
        
        for i, topic in enumerate(topics[:num_articles]):
            try:
                print(f"   Downloading article {i+1}/{num_articles}: {topic}")
                page = wikipedia.page(topic, auto_suggest=False)
                articles.append(page.content)
            except Exception as e:
                print(f"   [WARNING]  Skipped {topic}: {e}")
                continue
        
        text = "\n\n".join(articles)
        print(f"[OK] Downloaded {len(articles)} articles ({len(text):,} characters)")
        return text
        
    except ImportError:
        print("[WARNING]  Wikipedia API not installed. Using generated text instead.")
        return None


def generate_synthetic_text(target_tokens=500000):
    """
    Generate synthetic text to reach target token count.
    """
    print(f"[INFO] Generating synthetic text for ~{target_tokens:,} tokens...")
    
    # Base sentences with variety
    base_sentences = [
        "The quick brown fox jumps over the lazy dog.",
        "Natural language processing enables computers to understand human language.",
        "Machine learning algorithms learn patterns from data without explicit programming.",
        "Deep neural networks consist of multiple layers that process information hierarchically.",
        "Tokenization is the process of breaking text into smaller units called tokens.",
        "Embeddings represent words or tokens as dense vectors in high-dimensional space.",
        "Semantic similarity measures how closely related two pieces of text are in meaning.",
        "Vector databases store embeddings for fast similarity search and retrieval.",
        "Artificial intelligence systems can perform tasks that typically require human intelligence.",
        "Data science combines statistics, programming, and domain expertise to extract insights.",
        "Cloud computing provides on-demand access to computing resources over the internet.",
        "Software engineering involves designing, developing, and maintaining software systems.",
        "Web development encompasses creating websites and web applications using various technologies.",
        "Mobile applications are software programs designed to run on smartphones and tablets.",
        "Database systems organize and store data efficiently for quick retrieval and manipulation.",
        "Operating systems manage computer hardware and provide services for application programs.",
        "Computer networks connect devices to share resources and communicate with each other.",
        "Cybersecurity protects computer systems and networks from digital attacks and threats.",
        "Blockchain technology creates a distributed ledger that records transactions securely.",
        "Cryptocurrency is digital or virtual currency secured by cryptography.",
    ]
    
    # Generate text by repeating and varying sentences
    text_parts = []
    current_length = 0
    target_length = target_tokens * 5  # Rough estimate: ~5 chars per token
    
    while current_length < target_length:
        for sentence in base_sentences:
            # Add some variation
            variations = [
                sentence,
                sentence.lower(),
                sentence.upper(),
                sentence.capitalize(),
                sentence.replace(".", "!") if "." in sentence else sentence,
                sentence.replace(".", "?") if "." in sentence else sentence,
            ]
            
            for variant in variations:
                text_parts.append(variant)
                current_length += len(variant) + 2  # +2 for newline
                
                if current_length >= target_length:
                    break
            
            if current_length >= target_length:
                break
    
    text = "\n".join(text_parts)
    print(f"[OK] Generated {len(text):,} characters (~{len(text)//5:,} tokens)")
    return text


def load_text_file(file_path):
    """Load text from a file."""
    print(f"[INFO] Loading text from: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        print(f"[OK] Loaded {len(text):,} characters")
        return text
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        return None
    except PermissionError:
        print(f"[ERROR] Permission denied: {file_path}")
        return None
    except Exception as e:
        print(f"[ERROR] Error reading file: {e}")
        return None


def save_tokens(tokens, output_dir="workflow_output"):
    """Save tokens to disk for later use."""
    tokens_file = os.path.join(output_dir, "tokens.pkl")
    print(f"\n[INFO] Saving {len(tokens):,} tokens to {tokens_file}...")
    
    os.makedirs(output_dir, exist_ok=True)
    try:
        with open(tokens_file, 'wb') as f:
            pickle.dump(tokens, f)
        file_size = os.path.getsize(tokens_file) / (1024 * 1024)  # MB
        print(f"[OK] Tokens saved! File size: {file_size:.2f} MB")
        return tokens_file
    except Exception as e:
        print(f"[ERROR] Failed to save tokens: {e}")
        return None


def load_tokens(tokens_file):
    """Load tokens from disk."""
    print(f"\n[INFO] Loading tokens from {tokens_file}...")
    try:
        # Ensure correct import path is available for unpickling
        # Tokens may have been saved with references to core.core_tokenizer classes
        import sys
        import importlib
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent
        src_path = project_root / 'src'
        
        # Add paths to sys.path if not already there
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Create a custom unpickler that handles module path issues
        class CustomUnpickler(pickle.Unpickler):
            def find_class(self, module, name):
                # Handle old import paths that might be in the pickle
                if module == 'core.core_tokenizer' or module == 'core':
                    # Try to import from src.core.core_tokenizer instead
                    try:
                        from src.core.core_tokenizer import TokenRecord, TokenStream
                        if name == 'TokenRecord':
                            return TokenRecord
                        elif name == 'TokenStream':
                            return TokenStream
                    except ImportError:
                        pass
                
                # Fall back to default behavior
                return super().find_class(module, name)
        
        # Try to import the classes that might be referenced in the pickle
        try:
            from src.core.core_tokenizer import TokenRecord, TokenStream
        except ImportError:
            try:
                # Create a mock module if needed
                import types
                core_module = types.ModuleType('core')
                sys.modules['core'] = core_module
                core_tokenizer_module = types.ModuleType('core.core_tokenizer')
                sys.modules['core.core_tokenizer'] = core_tokenizer_module
                # Try to import and assign
                try:
                    from src.core.core_tokenizer import TokenRecord, TokenStream
                    core_tokenizer_module.TokenRecord = TokenRecord
                    core_tokenizer_module.TokenStream = TokenStream
                except ImportError:
                    pass
            except Exception:
                pass
        
        with open(tokens_file, 'rb') as f:
            try:
                # Try with custom unpickler first
                unpickler = CustomUnpickler(f)
                tokens = unpickler.load()
            except Exception:
                # Fall back to standard pickle.load
                f.seek(0)
                tokens = pickle.load(f)
        
        print(f"[OK] Loaded {len(tokens):,} tokens")
        return tokens
    except Exception as e:
        print(f"[ERROR] Failed to load tokens: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_embeddings_in_batches(tokens, embedding_gen, output_dir="workflow_output", batch_size=50000):
    """
    Generate embeddings in batches and save each batch to disk.
    This allows resuming if interrupted and avoids memory issues.
    """
    print("\n" + "=" * 80)
    print("GENERATING EMBEDDINGS IN BATCHES (with disk saving)")
    print("=" * 80)
    
    total_tokens = len(tokens)
    num_batches = (total_tokens + batch_size - 1) // batch_size
    
    print(f"Total tokens: {total_tokens:,}")
    print(f"Batch size: {batch_size:,} tokens per batch")
    print(f"Number of batches: {num_batches}")
    
    # Create batches directory
    batches_dir = os.path.join(output_dir, "embedding_batches")
    os.makedirs(batches_dir, exist_ok=True)
    
    batch_files = []
    processed_count = 0
    
    for batch_idx in range(num_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, total_tokens)
        batch_tokens = tokens[start_idx:end_idx]
        
        print(f"\n📦 Processing batch {batch_idx + 1}/{num_batches} (tokens {start_idx:,} to {end_idx:,})...")
        
        try:
            # Use smaller internal batch size to avoid memory issues in multiprocessing
            # The embedding generator handles multiprocessing internally with disk-based temp files
            internal_batch_size = min(5000, len(batch_tokens))  # Smaller batches for multiprocessing
            
            # Generate embeddings for this batch
            batch_embeddings = embedding_gen.generate_batch(batch_tokens, batch_size=internal_batch_size)
            
            # Save batch to disk
            batch_file = os.path.join(batches_dir, f"emb_batch_{batch_idx:04d}.npy")
            np.save(batch_file, batch_embeddings.astype(np.float32))
            batch_files.append(batch_file)
            
            file_size = os.path.getsize(batch_file) / (1024 * 1024)  # MB
            processed_count += len(batch_tokens)
            
            print(f"  [OK] Saved batch {batch_idx + 1}: {len(batch_tokens):,} tokens, {batch_embeddings.shape[1]} dims, {file_size:.2f} MB")
            print(f"  [INFO] Progress: {processed_count:,}/{total_tokens:,} tokens ({(processed_count/total_tokens*100):.1f}%)")
            
            # Cleanup
            del batch_embeddings, batch_tokens
            gc.collect()
            
        except Exception as e:
            print(f"  [ERROR] Error processing batch {batch_idx + 1}: {e}")
            print(f"  [WARNING]  You can resume from batch {batch_idx + 1} later")
            break
    
    # Save batch metadata
    metadata_file = os.path.join(output_dir, "embedding_batches_metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump({
            "total_tokens": total_tokens,
            "batch_size": batch_size,
            "num_batches": len(batch_files),
            "batch_files": batch_files,
            "embedding_dim": embedding_gen.embedding_dim
        }, f, indent=2)
    
    print(f"\n[OK] All batches saved! Metadata: {metadata_file}")
    print(f"   Total batches: {len(batch_files)}")
    print(f"   Total tokens processed: {processed_count:,}")
    
    return batch_files


def load_embedding_batches(batch_files, start_idx=0, end_idx=None):
    """Load embedding batches from disk."""
    if end_idx is None:
        end_idx = len(batch_files)
    
    print(f"\n[INFO] Loading embedding batches {start_idx} to {end_idx}...")
    embeddings_list = []
    
    for i in range(start_idx, min(end_idx, len(batch_files))):
        batch_file = batch_files[i]
        if os.path.exists(batch_file):
            batch_emb = np.load(batch_file)
            embeddings_list.append(batch_emb)
            print(f"  [OK] Loaded batch {i+1}: {batch_emb.shape}")
        else:
            print(f"  [WARNING]  Batch file not found: {batch_file}")
    
    if embeddings_list:
        all_embeddings = np.vstack(embeddings_list)
        print(f"[OK] Loaded {len(embeddings_list)} batches, total shape: {all_embeddings.shape}")
        return all_embeddings
    else:
        print("[ERROR] No batches loaded")
        return None


def test_full_workflow(text, output_dir="workflow_output", resume=False, max_batches_for_vector_store=5):
    """
    Test the complete workflow:
    1. Tokenization
    2. Embedding Generation
    3. Semantic Training
    4. Model Outcome (similarity search)
    
    Args:
        text: Input text to tokenize (can be None if resuming)
        output_dir: Directory to save outputs
        resume: Whether to resume from existing files
        max_batches_for_vector_store: Maximum number of batches to load into vector store (default: 5 = 250k tokens MAX)
                                      This limits memory usage. 
                                      CRITICAL: Very conservative default to prevent memory errors.
                                      Increase only if you have sufficient RAM (>8GB available).
    """
    print("\n" + "=" * 80)
    print("FULL WORKFLOW TEST: Tokenization -> Embedding -> Semantic -> Model Outcome")
    print("=" * 80)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize file paths (used in summary)
    tokenization_file = os.path.join(output_dir, "tokenization_results.json")
    embedding_file = os.path.join(output_dir, "embedding_stats.json")
    semantic_model_path = os.path.join(output_dir, "SOMA_semantic_model.pkl")
    search_file = os.path.join(output_dir, "similarity_search_results.json")
    
    # ============================================================================
    # STEP 1: TOKENIZATION (or load from disk if resuming)
    # ============================================================================
    print("\n" + "-" * 80)
    print("STEP 1: TOKENIZATION")
    print("-" * 80)
    
    tokens_file = os.path.join(output_dir, "tokens.pkl")
    
    if resume and os.path.exists(tokens_file):
        print("[INFO] Resuming: Loading tokens from disk...")
        all_tokens = load_tokens(tokens_file)
        if all_tokens is not None:
            print(f"[OK] Successfully loaded {len(all_tokens):,} tokens from disk!")
            print("   Skipping tokenization step - using existing tokens.")
        else:
            print("[ERROR] Failed to load tokens. Starting fresh tokenization...")
            resume = False
    else:
        all_tokens = None
    
    if all_tokens is None:
        if text is None:
            print("[ERROR] ERROR: Cannot tokenize - no text provided and tokens not found!")
            print("   Please provide text or ensure tokens.pkl exists in the output directory.")
            return
        print("Tokenizing with soma...")
        tokenizer = TextTokenizer(seed=42, embedding_bit=False)
        streams = tokenizer.build(text)
        
        # Collect all tokens
        all_tokens = []
        token_counts = {}
        for stream_name, token_stream in streams.items():
            tokens = token_stream.tokens
            all_tokens.extend(tokens)
            token_counts[stream_name] = len(tokens)
            print(f"  {stream_name}: {len(tokens):,} tokens")
        
        print(f"\n[OK] Total tokens: {len(all_tokens):,}")
        
        # Save tokens to disk for later use
        save_tokens(all_tokens, output_dir)
        
        # Save tokenization results (metadata)
        try:
            with open(tokenization_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "total_tokens": len(all_tokens),
                    "token_counts": token_counts,
                    "sample_tokens": [
                        {
                            "text": getattr(t, 'text', ''),
                            "uid": str(getattr(t, 'uid', 0)),
                            "stream": getattr(t, 'stream', ''),
                        }
                        for t in all_tokens[:100]  # First 100 tokens
                    ]
                }, f, indent=2)
            print(f"[INFO] Tokenization metadata saved to: {tokenization_file}")
        except Exception as e:
            print(f"[WARNING]  Failed to save tokenization metadata: {e}")
    
    # ============================================================================
    # STEP 2: EMBEDDING GENERATION (in batches, saved to disk)
    # ============================================================================
    print("\n" + "-" * 80)
    print("STEP 2: EMBEDDING GENERATION (BATCHED WITH DISK SAVING)")
    print("-" * 80)
    
    print("Initializing embedding generator...")
    embedding_gen = SOMAEmbeddingGenerator(
        strategy="feature_based",
        embedding_dim=768
    )
    
    # Check if embeddings already exist
    metadata_file = os.path.join(output_dir, "embedding_batches_metadata.json")
    batches_dir = os.path.join(output_dir, "embedding_batches")
    batch_files = []
    
    if resume and os.path.exists(metadata_file):
        print("[INFO] Resuming: Loading embedding batch metadata...")
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            batch_files = metadata.get("batch_files", [])
            
            # Check which batches exist
            existing_batches = [f for f in batch_files if os.path.exists(f)]
            print(f"  Found {len(existing_batches)}/{len(batch_files)} existing batches")
            
            if len(batch_files) == 0:
                print("[WARNING]  No batch files in metadata. Starting fresh embedding generation...")
                batch_files = []  # Will trigger generation below
            elif len(existing_batches) == len(batch_files) and len(batch_files) > 0:
                print(f"[OK] All {len(batch_files)} embedding batches already exist! Skipping generation.")
                print(f"   Total tokens in batches: {metadata.get('total_tokens', 'unknown'):,}")
                batch_files = existing_batches  # Use only existing batches
            else:
                print(f"[WARNING]  Only {len(existing_batches)}/{len(batch_files)} batches found. Regenerating missing batches...")
                # Find missing batches and regenerate
                missing_indices = [i for i, f in enumerate(batch_files) if not os.path.exists(f)]
                if missing_indices:
                    batch_size = metadata.get("batch_size", 50000)
                    os.makedirs(batches_dir, exist_ok=True)
                    # Regenerate missing batches
                    for idx in missing_indices:
                        start_idx = idx * batch_size
                        end_idx = min(start_idx + batch_size, len(all_tokens))
                        batch_tokens = all_tokens[start_idx:end_idx]
                        
                        print(f"  Regenerating batch {idx + 1}/{len(batch_files)}...")
                        try:
                            batch_embeddings = embedding_gen.generate_batch(batch_tokens, batch_size=min(10000, len(batch_tokens)))
                            batch_file = os.path.join(batches_dir, f"emb_batch_{idx:04d}.npy")
                            np.save(batch_file, batch_embeddings.astype(np.float32))
                            batch_files[idx] = batch_file  # Update with correct path
                            print(f"    [OK] Saved batch {idx + 1}")
                            del batch_embeddings
                            gc.collect()
                        except Exception as e:
                            print(f"    [ERROR] Error regenerating batch {idx + 1}: {e}")
                            continue
                
                # Update batch_files to only include existing ones
                batch_files = [f for f in batch_files if os.path.exists(f)]
        except Exception as e:
            print(f"[WARNING]  Error reading metadata: {e}. Starting fresh embedding generation...")
            batch_files = []
    
    # Generate embeddings if no batches exist
    if len(batch_files) == 0:
        print("[START] Starting embedding generation...")
        # Generate embeddings in batches and save to disk
        # Use 50k-100k tokens per batch for optimal speed/memory balance
        if len(all_tokens) > 1000000:
            batch_size = 100000  # 100k for very large datasets
        elif len(all_tokens) > 500000:
            batch_size = 75000   # 75k for large datasets
        else:
            batch_size = 50000   # 50k for medium datasets
        
        batch_files = generate_embeddings_in_batches(
            all_tokens, 
            embedding_gen, 
            output_dir, 
            batch_size=batch_size
        )
    
    # Load first batch to get stats
    if batch_files and len(batch_files) > 0:
        # Filter to only existing batch files
        existing_batch_files = [f for f in batch_files if os.path.exists(f)]
        if existing_batch_files:
            try:
                sample_emb = np.load(existing_batch_files[0])
                embedding_dim = sample_emb.shape[1]
                
                # Save embedding stats
                try:
                    with open(embedding_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "strategy": "feature_based",
                            "embedding_dim": embedding_dim,
                            "num_batches": len(existing_batch_files),
                            "total_tokens": len(all_tokens),
                            "embedding_sample": sample_emb[0].tolist()[:10] if len(sample_emb) > 0 else []
                        }, f, indent=2)
                    print(f"[INFO] Embedding stats saved to: {embedding_file}")
                except Exception as e:
                    print(f"[WARNING]  Failed to save embedding stats: {e}")
            except Exception as e:
                print(f"[WARNING]  Error loading sample embedding: {e}")
                embedding_dim = 768  # Default
        else:
            print("[WARNING]  No existing batch files found. Embeddings need to be generated.")
            embedding_dim = 768  # Default
    else:
        print("[WARNING]  No batch files available. Embeddings need to be generated.")
        embedding_dim = 768  # Default
        batch_files = []
    
    # ============================================================================
    # STEP 3: SEMANTIC TRAINING (Optional - can be forced even for large datasets)
    # ============================================================================
    print("\n" + "-" * 80)
    print("STEP 3: SEMANTIC TRAINING (Optional)")
    print("-" * 80)

    # Force flag for testing - DISABLED by default to avoid memory issues
    FORCE_SEMANTIC_TRAINING = False   # Set to True only if you have enough RAM (>16GB)
    
    # Aggressive limit - skip semantic training for datasets > 1M tokens
    SEMANTIC_TRAINING_TOKEN_LIMIT = 1_000_000  # Reduced to 1M tokens
    
    # Maximum vocabulary size for semantic training (prevents memory errors)
    MAX_VOCAB_SIZE_FOR_SEMANTIC = 50_000  # Limit to 50k most frequent tokens
    
    # If too large, skip semantic training (memory-intensive)
    if len(all_tokens) > SEMANTIC_TRAINING_TOKEN_LIMIT and not FORCE_SEMANTIC_TRAINING:
        print(f"[WARNING] Skipping semantic training for large dataset ({len(all_tokens):,} tokens > {SEMANTIC_TRAINING_TOKEN_LIMIT:,})")
        print("   Semantic training requires building co-occurrence matrix which")
        print("   can be memory-intensive for large vocabularies.")
        print("   Use feature-based embeddings instead.")
        print(f"   To enable, set FORCE_SEMANTIC_TRAINING = True (requires >16GB RAM)")
        semantic_embeddings = []
    else:
        try:
            print("Training semantic embeddings from soma structure...")
            # AGGRESSIVE VOCABULARY LIMITING to prevent memory errors
            trainer = SOMASemanticTrainer(
                embedding_dim=768,
                window_size=5,
                epochs=5,  # Reduced epochs to save memory
                max_vocab_size=MAX_VOCAB_SIZE_FOR_SEMANTIC  # CRITICAL: Limit vocabulary to 50k tokens
            )

            print("  - Building vocabulary...")
            trainer.build_vocab(all_tokens)
            vocab_size = len(trainer.vocab)
            print(f"    Vocabulary size: {vocab_size:,} (limited to {MAX_VOCAB_SIZE_FOR_SEMANTIC:,} most frequent)")
            
            # Check memory requirements before proceeding
            # Estimate: vocab_size * embedding_dim * 4 bytes (float32) * 2 (token + context embeddings)
            estimated_memory_gb = (vocab_size * 768 * 4 * 2) / (1024**3)
            print(f"    Estimated memory: ~{estimated_memory_gb:.2f} GB for embeddings")
            
            if estimated_memory_gb > 8.0:
                print(f"  [WARNING] Estimated memory ({estimated_memory_gb:.2f} GB) exceeds safe limit (8 GB)")
                print("   Reducing vocabulary size further...")
                # Force lower vocabulary size
                raise MemoryError(f"Vocabulary too large ({vocab_size:,} tokens). Requires {estimated_memory_gb:.2f} GB RAM.")

            # Additional guardrail — cap actual training tokens if dataset is too large
            MAX_TRAIN_TOKENS = min(200_000, len(all_tokens))  # Reduced to 200k tokens max
            print(f"  - Using {MAX_TRAIN_TOKENS:,} tokens for semantic training sample")

            # Build co-occurrence matrix
            trainer.build_cooccurrence(all_tokens[:MAX_TRAIN_TOKENS])
            if getattr(trainer, "cooccurrence_dict", None) is not None:
                print(f"    Co-occurrence pairs: {len(trainer.cooccurrence_dict):,}")
            else:
                print(f"    Co-occurrence matrix: {getattr(trainer, 'cooccurrence_matrix', 'N/A')}")

            print("  - Training embeddings...")
            trainer.train(all_tokens[:MAX_TRAIN_TOKENS])

            print(f"  - Saving model to {semantic_model_path}...")
            trainer.save(semantic_model_path)
            print("[OK] Semantic model trained and saved!")

            # Generate semantic embeddings (sample)
            print("\nGenerating semantic embeddings (sample)...")
            semantic_embeddings = []
            semantic_uids = []
            sample_size = min(10_000, len(all_tokens))
            for token in all_tokens[:sample_size]:
                uid = getattr(token, "uid", 0)
                emb = trainer.get_embedding(uid)
                if emb is not None:
                    semantic_embeddings.append(emb)
                    semantic_uids.append(uid)

            print(f"[OK] Generated {len(semantic_embeddings):,} semantic embeddings")

        except MemoryError as e:
            print(f"[ERROR] Memory error during semantic training: {e}")
            print("   Skipping semantic training. Use feature-based embeddings instead.")
            semantic_embeddings = []
        except Exception as e:
            print(f"[ERROR] Error during semantic training: {e}")
            print("   Skipping semantic training. Use feature-based embeddings instead.")
            semantic_embeddings = []

    
    # ============================================================================
    # STEP 4: MODEL OUTCOME (Similarity Search)
    # ============================================================================
    print("\n" + "-" * 80)
    print("STEP 4: MODEL OUTCOME - SIMILARITY SEARCH")
    print("-" * 80)
    
    # Use feature-based embeddings for vector store
    # CRITICAL: Use ChromaDB with persistence instead of FAISS for large datasets
    # ChromaDB uses disk storage and doesn't load everything into memory
    print("Creating vector store...")
    
    # Check if ChromaDB is available FIRST
    try:
        import chromadb
        CHROMA_AVAILABLE = True
    except ImportError:
        CHROMA_AVAILABLE = False
    
    use_chroma = False
    if CHROMA_AVAILABLE:
        print("[INFO] ChromaDB detected! Using disk-based storage (can load ALL batches)")
        try:
            from src.embeddings.vector_store import ChromaVectorStore
            # Use persistent storage - data stays on disk, not in memory
            persist_dir = os.path.join(output_dir, "chroma_db")
            
            # Optionally clear existing collection if resume=False
            # This prevents duplicate ID warnings when re-running
            if not resume:
                try:
                    import chromadb
                    temp_client = chromadb.PersistentClient(path=persist_dir)
                    try:
                        temp_client.delete_collection(name="SOMA_embeddings")
                        print("[INFO] Cleared existing ChromaDB collection for fresh start")
                    except Exception:
                        pass  # Collection might not exist yet
                except Exception:
                    pass  # Ignore errors during cleanup
            
            vector_store = ChromaVectorStore(
                embedding_dim=768,
                persist_directory=persist_dir,
                collection_name="SOMA_embeddings"
            )
            print(f"[OK] ChromaDB vector store created (persistent storage: {persist_dir})")
            use_chroma = True
        except Exception as e:
            print(f"[WARNING] Failed to create ChromaDB store: {e}")
            print("   Falling back to FAISS (memory-intensive, limited batches).")
            import traceback
            traceback.print_exc()
            vector_store = FAISSVectorStore(embedding_dim=768)
            use_chroma = False
    else:
        print("[WARNING] ChromaDB not installed. Using FAISS (memory-intensive, limited batches).")
        print("   To load ALL batches, install ChromaDB: pip install chromadb")
        print("   Without ChromaDB, only 3 batches (~300k tokens) will be loaded to avoid memory errors.")
        vector_store = FAISSVectorStore(embedding_dim=768)
        use_chroma = False
    
    # Filter to only existing batch files
    existing_batch_files = [f for f in batch_files if os.path.exists(f)] if batch_files else []
    
    if len(existing_batch_files) == 0:
        print("[ERROR] No embedding batches found! Cannot create vector store.")
        print("   Please generate embeddings first. The script will now generate them.")
        # Generate embeddings now
        if len(all_tokens) > 1000000:
            batch_size_gen = 100000
        elif len(all_tokens) > 500000:
            batch_size_gen = 75000
        else:
            batch_size_gen = 50000
        
        batch_files = generate_embeddings_in_batches(
            all_tokens, 
            embedding_gen, 
            output_dir, 
            batch_size=batch_size_gen
        )
        existing_batch_files = [f for f in batch_files if os.path.exists(f)]
        
        if len(existing_batch_files) == 0:
            print("[ERROR] Failed to generate embeddings. Cannot proceed with similarity search.")
            return
    
    # Load metadata to get batch_size (needed for batch limiting calculation)
    metadata = {"batch_size": 50000}
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        except Exception as e:
            print(f"[WARNING]  Error reading metadata: {e}. Using default batch size.")
    
    actual_batch_size = metadata.get('batch_size', 100000)  # Default to 100k if not found
    
    # CRITICAL: Check ChromaDB FIRST, then decide batch loading strategy
    if use_chroma:
        # ChromaDB: Load ALL batches (disk storage, no memory limit)
        batches_to_load = existing_batch_files
        estimated_tokens = len(batches_to_load) * actual_batch_size
        estimated_memory_gb = 0  # ChromaDB doesn't load everything into memory
        print(f"\n[INFO] ChromaDB Mode: Loading ALL {len(batches_to_load)} batches")
        print(f"   Total tokens: ~{estimated_tokens:,}")
        print(f"   Data stored on disk: {os.path.join(output_dir, 'chroma_db')}")
        print(f"   No memory limit (disk-based storage)")
    else:
        # FAISS: Enforce strict memory limits (memory-based)
        print(f"\n[INFO] FAISS Mode: Memory-based storage (strict limits)")
        max_safe_tokens = 300_000  # ULTRA CONSERVATIVE: ~900 MB (300k tokens × 768 × 4 bytes)
        max_safe_batches_from_tokens = max_safe_tokens // actual_batch_size
        if max_safe_batches_from_tokens < 1:
            max_safe_batches_from_tokens = 1
        
        # Use the MORE RESTRICTIVE of: max_batches_for_vector_store OR max_safe_batches_from_tokens
        final_max_batches = min(max_batches_for_vector_store, max_safe_batches_from_tokens, len(existing_batch_files))
        batches_to_load = existing_batch_files[:final_max_batches]
        
        # Recalculate with final batch count
        estimated_tokens = len(batches_to_load) * actual_batch_size
        estimated_memory_gb = (estimated_tokens * 768 * 4) / (1024**3)
        
        print(f"   Batches to load: {len(batches_to_load)}/{len(existing_batch_files)}")
        print(f"   Actual batch size: {actual_batch_size:,} tokens per batch")
        print(f"   Estimated tokens: ~{estimated_tokens:,}")
        print(f"   Estimated memory: ~{estimated_memory_gb:.2f} GB")
        print(f"   [WARNING] Limited due to memory constraints (FAISS loads everything into RAM)")
        
        if len(existing_batch_files) > len(batches_to_load):
            print(f"   Install ChromaDB for unlimited loading: pip install chromadb")
    
    # Optimize chunk size: ChromaDB max is 5461, use 5000 for safety and speed
    batch_size = 5000  # Same for both ChromaDB and FAISS
    total_tokens_added = 0
    
    # Only enforce memory limits for FAISS (memory-based)
    if not use_chroma:
        max_safe_tokens = 300_000  # ULTRA CONSERVATIVE for FAISS
    
    # Start loading batches
    print(f"\n[INFO] Starting to load batches into vector store...")
    print(f"   Processing {len(batches_to_load)} batches in chunks of {batch_size:,} tokens")
    
    # HARD LIMIT: Never exceed max_safe_tokens (only for FAISS)
    for batch_idx, batch_file in enumerate(batches_to_load):
        if not use_chroma:
            # Check memory before loading each batch (FAISS only)
            if total_tokens_added >= max_safe_tokens:
                print(f"  [WARNING] Reached safe token limit ({max_safe_tokens:,} tokens). Stopping batch loading.")
                break
            
            # Calculate how many tokens this batch would add
            expected_batch_tokens = actual_batch_size
            if total_tokens_added + expected_batch_tokens > max_safe_tokens:
                # Only load partial batch to stay under limit
                remaining_tokens = max_safe_tokens - total_tokens_added
                if remaining_tokens < 1000:  # Not worth loading less than 1k tokens
                    print(f"  [WARNING] Would exceed limit. Stopping at {total_tokens_added:,} tokens.")
                    break
                print(f"  [WARNING] Batch {batch_idx + 1} would exceed limit. Loading partial batch ({remaining_tokens:,} tokens)")
            
        try:
            # Load batch
            batch_embeddings = np.load(batch_file)
            batch_start = batch_idx * metadata.get("batch_size", 50000)
            batch_end = min(batch_start + len(batch_embeddings), len(all_tokens))
            batch_tokens = all_tokens[batch_start:batch_end]
            
            # Ensure we have enough tokens
            if len(batch_tokens) != len(batch_embeddings):
                batch_tokens = all_tokens[batch_start:batch_start + len(batch_embeddings)]
            
            # Skip if this batch would exceed safe limit (FAISS only)
            if not use_chroma and total_tokens_added + len(batch_tokens) > max_safe_tokens:
                remaining = max_safe_tokens - total_tokens_added
                if remaining > 1000:  # Only add if we have meaningful space left
                    batch_tokens = batch_tokens[:remaining]
                    batch_embeddings = batch_embeddings[:remaining]
                    print(f"  [WARNING] Truncating batch {batch_idx + 1} to stay under safe limit")
                else:
                    print(f"  [WARNING] Skipping batch {batch_idx + 1} (would exceed safe limit)")
                    del batch_embeddings, batch_tokens
                    gc.collect()
                    break
            
            # Add to vector store in chunks
            chunk_error = False
            num_chunks = (len(batch_tokens) + batch_size - 1) // batch_size
            
            # Log start of batch for first batch or every 10th batch (to show progress)
            if use_chroma and ((batch_idx + 1) == 1 or (batch_idx + 1) % 10 == 0):
                print(f"  [INFO] Loading batch {batch_idx + 1}/{len(batches_to_load)} ({len(batch_tokens):,} tokens, {num_chunks} chunks)...")
            
            for chunk_idx, chunk_start in enumerate(range(0, len(batch_tokens), batch_size)):
                chunk_end = min(chunk_start + batch_size, len(batch_tokens))
                chunk_tokens = batch_tokens[chunk_start:chunk_end]
                chunk_embeddings = batch_embeddings[chunk_start:chunk_end]
                
                try:
                    vector_store.add_tokens(chunk_tokens, chunk_embeddings)
                except MemoryError as me:
                    print(f"  [ERROR] Memory error adding batch {batch_idx + 1}, chunk {chunk_idx + 1}/{num_chunks}: {me}")
                    print(f"  [WARNING]  Stopping here to avoid OOM. Loaded {total_tokens_added:,} tokens so far.")
                    # Clean up before breaking
                    del chunk_tokens, chunk_embeddings
                    gc.collect()
                    chunk_error = True
                    break  # Break inner loop
                except Exception as e:
                    # For ChromaDB, reduce chunk size if batch size error
                    if use_chroma and "max batch size" in str(e).lower():
                        # Try smaller chunk
                        smaller_chunk_size = min(4000, len(chunk_tokens))
                        if smaller_chunk_size > 0:
                            try:
                                vector_store.add_tokens(
                                    chunk_tokens[:smaller_chunk_size], 
                                    chunk_embeddings[:smaller_chunk_size]
                                )
                                # Add remaining in next iteration
                                if smaller_chunk_size < len(chunk_tokens):
                                    # This shouldn't happen often, but handle it
                                    print(f"  [WARNING] Had to split chunk further (ChromaDB limit)")
                                    continue
                            except Exception as e2:
                                print(f"  [WARNING] Error with smaller chunk: {e2}")
                                continue
                        else:
                            print(f"  [WARNING] Chunk too small after reduction, skipping")
                            continue
                    else:
                        print(f"  [WARNING] Error adding chunk {chunk_idx + 1}/{num_chunks}: {e}")
                        # Continue with next chunk
                        continue
            
            # If chunk error occurred, break from batch loop too
            if chunk_error:
                del batch_embeddings, batch_tokens
                gc.collect()
                break
            
            total_tokens_added += len(batch_tokens)
            
            # Optimized progress logging: Less verbose for ChromaDB (loading many batches)
            if use_chroma:
                # Log first batch, then every 10 batches for ChromaDB (since loading all 117 batches)
                if (batch_idx + 1) == 1 or (batch_idx + 1) % 10 == 0 or (batch_idx + 1) == len(batches_to_load):
                    progress_pct = ((batch_idx + 1) / len(batches_to_load)) * 100
                    print(f"  [OK] Added batch {batch_idx + 1}/{len(batches_to_load)} ({total_tokens_added:,} tokens, {progress_pct:.1f}% complete)")
                elif (batch_idx + 1) % 5 == 0:
                    # Also log every 5 batches with a simpler message
                    print(f"  [INFO] Processing batch {batch_idx + 1}/{len(batches_to_load)} ({total_tokens_added:,} tokens)...")
            else:
                # Log every batch for FAISS (fewer batches)
                print(f"  [OK] Added batch {batch_idx + 1}/{len(batches_to_load)} ({total_tokens_added:,} tokens total)")
            
            # Cleanup after each batch
            del batch_embeddings, batch_tokens
            gc.collect()
            
            # Check if we've hit the limit (FAISS only)
            if not use_chroma and total_tokens_added >= max_safe_tokens:
                print(f"  [WARNING] Reached safe token limit. Stopping batch loading.")
                break
            
        except MemoryError as me:
            print(f"  [ERROR] Memory error processing batch {batch_idx + 1}: {me}")
            print(f"  [WARNING]  Stopped loading batches. Loaded {total_tokens_added:,} tokens into vector store.")
            # Clean up
            try:
                del batch_embeddings, batch_tokens
            except Exception:
                pass
            gc.collect()
            break
        except Exception as e:
            print(f"  [WARNING]  Error processing batch {batch_idx + 1}: {e}")
            # Clean up
            try:
                del batch_embeddings, batch_tokens
            except Exception:
                pass
            gc.collect()
            # Continue with next batch
            continue
    
    if total_tokens_added == 0:
        print("[ERROR] No embeddings were added to vector store!")
        return
    
    print("[OK] Vector store created!")
    
    # Test similarity search
    print("\nTesting similarity search...")
    try:
        # Load first batch to get query embedding
        if len(batches_to_load) > 0:
            query_emb = np.load(batches_to_load[0])
            query_embedding = query_emb[0] if len(query_emb) > 0 else None
            
            if query_embedding is None:
                print("[WARNING]  No query embedding available. Skipping similarity search.")
                results = []
            else:
                results = vector_store.search(query_embedding, top_k=10)
        else:
            print("[WARNING]  No batch files available for query. Skipping similarity search.")
            results = []
    except Exception as e:
        print(f"[WARNING]  Error loading query embedding: {e}")
        results = []
    
    if results:
        print(f"\nTop 10 similar tokens to '{getattr(all_tokens[0], 'text', '')}':")
        for i, result in enumerate(results, 1):
            # FAISSVectorStore returns 'text' directly, not in 'metadata'
            result_text = result.get('text', result.get('metadata', {}).get('text', 'N/A'))
            result_distance = result.get('distance', 0.0)
            print(f"  {i}. {result_text} (distance: {result_distance:.4f})")
    else:
        print("[WARNING]  No search results found")
    
    # Save search results
    try:
        with open(search_file, 'w', encoding='utf-8') as f:
            # Handle both FAISSVectorStore format (text directly) and ChromaVectorStore format (in metadata)
            formatted_results = []
            for r in results:
                result_text = r.get('text', r.get('metadata', {}).get('text', 'N/A'))
                result_metadata = r.get('metadata', {})
                formatted_results.append({
                    "text": result_text,
                    "distance": r.get('distance', 0.0),
                    "uid": result_metadata.get('uid', 'N/A')
                })
            
            json.dump({
                "query": getattr(all_tokens[0], 'text', ''),
                "results": formatted_results
            }, f, indent=2)
        print(f"[INFO] Search results saved to: {search_file}")
    except Exception as e:
        print(f"[WARNING]  Failed to save search results: {e}")
    
    # ============================================================================
    # SUMMARY
    # ============================================================================
    print("\n" + "=" * 80)
    print("[OK] WORKFLOW COMPLETE!")
    print("=" * 80)
    print(f"\nResults saved to: {output_dir}/")
    if os.path.exists(tokenization_file):
        print(f"  - Tokenization: {tokenization_file}")
    if os.path.exists(embedding_file):
        print(f"  - Embeddings: {embedding_file}")
    if os.path.exists(semantic_model_path):
        print(f"  - Semantic Model: {semantic_model_path}")
    if os.path.exists(search_file):
        print(f"  - Similarity Search: {search_file}")
    print(f"\nTotal tokens processed: {len(all_tokens):,}")
    if batch_files and len(batch_files) > 0:
        existing_batch_files = [f for f in batch_files if os.path.exists(f)]
        if existing_batch_files:
            try:
                sample_emb = np.load(existing_batch_files[0])
                print(f"Embedding dimension: {sample_emb.shape[1]}")
                print(f"Embedding batches available: {len(existing_batch_files)}")
                if len(existing_batch_files) > max_batches_for_vector_store:
                    print(f"  [WARNING]  Note: Only first {max_batches_for_vector_store} batches loaded into vector store")
                    print(f"      (to avoid memory issues). All {len(existing_batch_files)} batches are on disk.")
            except Exception:
                pass
    print(f"Semantic embeddings: {len(semantic_embeddings):,}")
    if 'total_tokens_added' in locals():
        print(f"Tokens in vector store: {total_tokens_added:,} (for similarity search)")


def main():
    """Main function."""
    import sys
    
    print("=" * 80)
    print("SOMA Full Workflow Test - 500k Tokens")
    print("=" * 80)
    
    # Check dependencies first
    if not check_and_install_dependencies():
        print("\n[WARNING]  Some dependencies are missing. Please install them manually.")
        return
    
    # Support command-line arguments for Railway compute (non-interactive mode)
    # Usage: python test_full_workflow_500k.py [output_dir] [resume] [choice] [file_path]
    # Example: python test_full_workflow_500k.py workflow_output n 2
    # Example: python test_full_workflow_500k.py workflow_output n 3 /path/to/file.txt
    
    if len(sys.argv) > 1:
        # Non-interactive mode (Railway compute)
        output_dir = sys.argv[1] if len(sys.argv) > 1 else "workflow_output"
        resume_input = sys.argv[2].lower() if len(sys.argv) > 2 else "n"
        choice = sys.argv[3] if len(sys.argv) > 3 else "2"
        resume = resume_input == 'y'
        print(f"\n[Non-interactive mode]")
        print(f"  Output directory: {output_dir}")
        print(f"  Resume: {resume}")
        print(f"  Data source choice: {choice}")
    else:
        # Interactive mode (local development)
        output_dir = "workflow_output"
        
        # Check if we can resume
        tokens_file = os.path.join(output_dir, "tokens.pkl")
        resume = os.path.exists(tokens_file)
        
        if resume:
            print("\n[INFO] Found existing tokens. You can resume from where you left off.")
            try:
                resume_choice = input("Resume? (y/n) [default: y]: ").strip().lower() or "y"
                resume = resume_choice == "y"
            except (EOFError, KeyboardInterrupt):
                # Non-interactive fallback
                resume = True
                print("\n[Non-interactive] Defaulting to: resume")
        
        if not resume:
            print("\nChoose data source:")
            print("1. Download Wikipedia articles (requires: pip install wikipedia-api)")
            print("2. Generate synthetic text")
            print("3. Load from file")
            print("4. Use sample text (small test)")
            
            try:
                choice = input("\nEnter choice (1-4) [default: 2]: ").strip() or "2"
            except (EOFError, KeyboardInterrupt):
                # Non-interactive fallback
                choice = "2"
                print("\n[Non-interactive] Defaulting to: Generate synthetic text (choice 2)")
    
    # Process choice (works for both interactive and non-interactive)
    if not resume:
        text = None
        
        if choice == "1":
            text = download_wikipedia_sample(num_articles=50)
            if text is None:
                print("Falling back to synthetic text...")
                text = generate_synthetic_text(target_tokens=500000)
        
        elif choice == "2":
            text = generate_synthetic_text(target_tokens=500000)
        
        elif choice == "3":
            if len(sys.argv) > 4:
                # Non-interactive: file path from command line
                file_path = sys.argv[4]
            else:
                # Interactive: prompt for file path
                try:
                    file_path = input("Enter file path: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("[ERROR] File path required but input not available. Use: python test_full_workflow_500k.py <output_dir> <resume> 3 <file_path>")
                    return
            
            if os.path.exists(file_path):
                text = load_text_file(file_path)
            else:
                print(f"[ERROR] File not found: {file_path}")
                return
        
        elif choice == "4":
            # Small test
            text = """
            Natural language processing is a field of artificial intelligence.
            Machine learning models learn patterns from data.
            Deep learning uses neural networks with multiple layers.
            Tokenization is the process of breaking text into tokens.
            Embeddings represent tokens as dense vectors.
            Semantic embeddings capture meaning and relationships.
            """ * 1000  # Repeat to get more tokens
            print(f"Using sample text ({len(text):,} characters)")
        
        else:
            print("Invalid choice. Using synthetic text...")
            text = generate_synthetic_text(target_tokens=500000)
        
        if not text:
            print("[ERROR] Failed to load text data")
            return
    else:
        text = None  # Not needed if resuming
    
    # Run full workflow
    test_full_workflow(text, output_dir=output_dir, resume=resume)


if __name__ == "__main__":
    main()
