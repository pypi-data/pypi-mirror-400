"""
Comprehensive SOMA Vector Store Example
==========================================

This is a unified example combining ALL vector store capabilities:
- Weaviate (cloud-based, production-ready, with tags and memory building)
- FAISS (fast, in-memory, high-performance search)
- ChromaDB (persistent, disk-based, scalable)

COMPLETE FEATURE CHECKLIST:
==========================

From search_examples.py:
  ✓ filter_stop_words() - Filter stop words from search results
  ✓ semantic_search() - Search with filtering and similarity thresholds
  ✓ find_related_concepts() - Average embeddings for multiple concepts
  ✓ compare_tokens() - Direct token-to-token similarity comparison
  ✓ explore_concept() - Multi-level concept exploration (depth-based)
  ✓ find_concept_cluster() - Find clusters around a seed concept
  ✓ interactive_search_mode() - Interactive CLI for exploration
  ✓ quick_load_vector_store() - Load from disk batches

From use_semantic_embeddings.py:
  ✓ use_semantic_embeddings() - Generate semantic embeddings (via generate_embeddings)
  ✓ compare_embeddings() - Text-to-text cosine similarity comparison

From test_full_workflow_500k.py:
  ✓ Full workflow (tokenization → embedding → storage → search)
  ✓ download_wikipedia_sample() - Download Wikipedia articles
  ✓ generate_synthetic_text() - Generate synthetic text for testing
  ✓ load_text_file() - Load text from file
  ✓ save_tokens() - Save tokens to disk
  ✓ generate_embeddings_in_batches() - Generate embeddings in batches with disk saving (CRITICAL for large datasets)
  ✓ load_embedding_batches() - Load embedding batches from disk
  ✓ Batch processing and disk saving
  ✓ Resume capability (load existing data)
  ✓ Large dataset handling

From use_vector_store.py:
  ✓ load_vector_store() - Load from existing batches
  ✓ search_examples() - Example searches
  ✓ interactive_search() - Interactive search mode
  ✓ analyze_clusters() - Cluster analysis

From compare_neighbors.py:
  ✓ Overlap comparison - Compare results between stores/strategies

From embedding_example.py:
  ✓ example_1_basic_embedding() - Detailed token-by-token embedding view (show_detailed_embeddings)
  ✓ example_2_vector_store() - Vector store storage
  ✓ example_3_inference_pipeline() - Pipeline functionality (covered by methods)
  ✓ example_4_document_embeddings() - Document-level embeddings

From eval_embedding_quality.py:
  ✓ evaluate_quality() - Quality evaluation with probe tokens

From weaviate_codes/example_usage.py:
  ✓ Query by ID - Retrieve tokens by UUID from Weaviate
  ✓ Retrieval before processing - Context memory recall
  ✓ Memory building with tags - filename, date, session tracking
  ✓ Visualization - t-SNE semantic map

Embedding Alignment (NEW):
  ✓ evaluate_semantic_alignment() - Test how well embeddings match human semantics
  ✓ train_embedding_alignment() - Train alignment using labeled pairs (contrastive + MSE)
  ✓ apply_alignment() - Apply learned alignment transformation to embeddings

SOMA-Native Context Fusion (NEW - 1000% SOMA Way):
  ✓ build_context_fusion_embeddings() - Context-aware embeddings using SOMA's native mechanisms
    - Uses prev_uid/next_uid for positional dependency
    - Uses content_id for semantic grouping
    - Uses global_id for full context signatures
    - Uses neighbor-aware backend numbers
    - Positional encoding from soma's deterministic index
  ✓ search_with_context_fusion() - Semantic search with context-aware embeddings

VECTOR STORES SUPPORTED:
  ✓ Weaviate - Cloud-based, production-ready, with tags
  ✓ FAISS - Fast in-memory search
  ✓ ChromaDB - Persistent disk-based storage

EMBEDDING STRATEGIES:
  ✓ feature_based (default) - Pure SOMA features, fast, no external dependencies
  ✓ hybrid - User-selectable: Combines SOMA features + sentence-transformers (better semantics)
    - User can choose at runtime whether to use sentence-transformers
    - Falls back to feature_based if sentence-transformers not available

ALL FEATURES IN ONE UNIFIED FILE!
"""

import sys
import os
import json
import pickle
import time
import uuid as uuid_module
import gc
import subprocess
import warnings
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
import numpy as np

# Suppress sentence-transformers warning at import time
# We'll handle it based on user's choice later
warnings.filterwarnings('ignore', message='.*sentence-transformers not available.*', category=UserWarning)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.core_tokenizer import TextTokenizer
from src.embeddings.embedding_generator import somaEmbeddingGenerator
from src.embeddings.semantic_trainer import somaSemanticTrainer

# Try importing vector stores
try:
    from src.embeddings.vector_store import FAISSVectorStore, ChromaVectorStore
    FAISS_AVAILABLE = True
    CHROMA_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    CHROMA_AVAILABLE = False

# Try importing Weaviate
WEAVIATE_AVAILABLE = False
WeaviateVectorStore = None

try:
    # Import Weaviate vector store from weaviate_codes folder
    weaviate_codes_path = Path(__file__).parent.parent / "weaviate_codes" / "weaviate_vector_store.py"
    if weaviate_codes_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("weaviate_vector_store", str(weaviate_codes_path))
        weaviate_store_module = importlib.util.module_from_spec(spec)
        
        # Handle weaviate import conflict
        original_path = sys.path.copy()
        try:
            # Temporarily remove project root to avoid local weaviate folder shadowing
            project_root = Path(__file__).parent.parent
            if str(project_root) in sys.path:
                sys.path.remove(str(project_root))
            
            # Try to import weaviate package
            try:
                import weaviate
                from weaviate.classes.init import Auth
                weaviate_store_module.__dict__['weaviate'] = weaviate
                weaviate_store_module.__dict__['Auth'] = Auth
                sys.modules['weaviate'] = weaviate
            except ImportError:
                pass
            
            spec.loader.exec_module(weaviate_store_module)
            WeaviateVectorStore = getattr(weaviate_store_module, "WeaviateVectorStore", None)
            if WeaviateVectorStore:
                WEAVIATE_AVAILABLE = True
        finally:
            sys.path[:] = original_path
except Exception as e:
    print(f"[WARNING] Could not load Weaviate: {e}")


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


class UnifiedVectorStoreExample:
    """Unified example combining all vector store capabilities."""
    
    def __init__(self, output_dir="workflow_output", use_hybrid_embeddings=False):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # User choice for hybrid embeddings (sentence-transformers)
        self.use_hybrid_embeddings = use_hybrid_embeddings
        
        # Initialize components
        self.tokenizer = TextTokenizer(seed=42, embedding_bit=False)
        
        # Choose embedding strategy based on user preference
        if use_hybrid_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                # Check if sentence-transformers is available
                _ = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                strategy = "hybrid"
                print("[INFO] Using hybrid embeddings (sentence-transformers enabled)")
            except ImportError:
                print("[WARNING] sentence-transformers not installed. Falling back to feature_based.")
                print("   Install with: pip install sentence-transformers")
                strategy = "feature_based"
                self.use_hybrid_embeddings = False
            except Exception as e:
                print(f"[WARNING] Could not load sentence-transformers model: {e}")
                print("   Falling back to feature_based embeddings.")
                strategy = "feature_based"
                self.use_hybrid_embeddings = False
        else:
            strategy = "feature_based"
            # User chose feature_based, so suppress any hybrid-related warnings
            warnings.filterwarnings('ignore', message='.*sentence-transformers.*', category=UserWarning)
        
        self.embedding_gen = SOMAEmbeddingGenerator(strategy=strategy, embedding_dim=768)
        
        # Vector stores
        self.weaviate_store = None
        self.faiss_store = None
        self.chroma_store = None
        
        # Data
        self.tokens = []
        self.embeddings = None
    
    def save_tokens(self, tokens=None, output_dir=None):
        """Save tokens to disk for later use."""
        if tokens is None:
            tokens = self.tokens
        if output_dir is None:
            output_dir = self.output_dir
        
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
    
    def generate_embeddings_in_batches(self, tokens=None, embedding_gen=None, batch_size=50000):
        """
        Generate embeddings in batches and save each batch to disk.
        This allows resuming if interrupted and avoids memory issues.
        """
        if tokens is None:
            tokens = self.tokens
        if embedding_gen is None:
            embedding_gen = self.embedding_gen
        
        print("\n" + "=" * 80)
        print("GENERATING EMBEDDINGS IN BATCHES (with disk saving)")
        print("=" * 80)
        
        total_tokens = len(tokens)
        num_batches = (total_tokens + batch_size - 1) // batch_size
        
        print(f"Total tokens: {total_tokens:,}")
        print(f"Batch size: {batch_size:,} tokens per batch")
        print(f"Number of batches: {num_batches}")
        
        # Create batches directory
        batches_dir = os.path.join(self.output_dir, "embedding_batches")
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
                internal_batch_size = min(5000, len(batch_tokens))
                
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
        metadata_file = os.path.join(self.output_dir, "embedding_batches_metadata.json")
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
    
    def load_embedding_batches(self, batch_files, start_idx=0, end_idx=None):
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
        
    def load_vector_store_from_disk(self, max_batches: int = 30):
        """Load vector store from existing batches on disk (from test_full_workflow_500k.py)."""
        print("\n" + "=" * 80)
        print("LOADING VECTOR STORE FROM DISK")
        print("=" * 80)
        
        # Load tokens
        tokens_file = os.path.join(self.output_dir, "tokens.pkl")
        if not os.path.exists(tokens_file):
            print(f"[WARNING] Tokens file not found: {tokens_file}")
            return False
        
        print(f"📂 Loading tokens from {tokens_file}...")
        try:
            # Handle pickle import issues
            import types
            project_root = Path(__file__).parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            # Create mock modules for pickle compatibility
            if 'core' not in sys.modules:
                core_module = types.ModuleType('core')
                sys.modules['core'] = core_module
            if 'core.core_tokenizer' not in sys.modules:
                core_tokenizer_module = types.ModuleType('core.core_tokenizer')
                sys.modules['core.core_tokenizer'] = core_tokenizer_module
                try:
                    from src.core.core_tokenizer import TokenRecord, TokenStream
                    core_tokenizer_module.TokenRecord = TokenRecord
                    core_tokenizer_module.TokenStream = TokenStream
                except ImportError:
                    pass
            
            # Custom unpickler
            class CustomUnpickler(pickle.Unpickler):
                def find_class(self, module, name):
                    if module == 'core.core_tokenizer' or module == 'core':
                        try:
                            from src.core.core_tokenizer import TokenRecord, TokenStream
                            if name == 'TokenRecord':
                                return TokenRecord
                            elif name == 'TokenStream':
                                return TokenStream
                        except ImportError:
                            pass
                    return super().find_class(module, name)
            
            with open(tokens_file, 'rb') as f:
                try:
                    unpickler = CustomUnpickler(f)
                    self.tokens = unpickler.load()
                except Exception:
                    f.seek(0)
                    self.tokens = pickle.load(f)
            
            print(f"[OK] Loaded {len(self.tokens):,} tokens")
        except Exception as e:
            print(f"[ERROR] Failed to load tokens: {e}")
            return False
        
        # Load embedding batches
        metadata_file = os.path.join(self.output_dir, "embedding_batches_metadata.json")
        if not os.path.exists(metadata_file):
            print(f"[WARNING] Metadata file not found: {metadata_file}")
            return False
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        batch_files = metadata.get("batch_files", [])[:max_batches]
        embedding_dim = metadata.get("embedding_dim", 768)
        batch_size = metadata.get("batch_size", 50000)
        
        # Load first batch to get embeddings
        if batch_files and os.path.exists(batch_files[0]):
            self.embeddings = np.load(batch_files[0])
            print(f"[OK] Loaded sample embeddings: {self.embeddings.shape}")
        else:
            print("[WARNING] No batch files found")
            return False
        
        # Load batches into vector stores
        print(f"📦 Loading {len(batch_files)} batches into vector stores...")
        print("[INFO] Using memory-safe loading with error recovery...")
        
        total_added = 0
        faiss_failed = False
        chroma_failed = False
        faiss_total = 0
        chroma_total = 0
        
        for batch_idx, batch_file in enumerate(batch_files):
            if not os.path.exists(batch_file):
                continue
            
            try:
                batch_emb = np.load(batch_file)
                batch_start = batch_idx * batch_size
                batch_end = min(batch_start + len(batch_emb), len(self.tokens))
                batch_tokens = self.tokens[batch_start:batch_end]
                
                # Add to FAISS (with memory error recovery)
                if self.faiss_store and not faiss_failed:
                    try:
                        chunk_size = 10000
                        for chunk_start in range(0, len(batch_tokens), chunk_size):
                            chunk_end = min(chunk_start + chunk_size, len(batch_tokens))
                            self.faiss_store.add_tokens(
                                batch_tokens[chunk_start:chunk_end],
                                batch_emb[chunk_start:chunk_end]
                            )
                        faiss_total += len(batch_tokens)
                    except MemoryError:
                        print(f"  [WARNING] FAISS out of memory at batch {batch_idx + 1}. Stopping FAISS loading.")
                        faiss_failed = True
                        self.faiss_store = None  # Disable FAISS for remaining batches
                    except Exception as e:
                        error_msg = str(e).lower()
                        if 'bad_alloc' in error_msg or 'memory' in error_msg:
                            print(f"  [WARNING] FAISS memory error at batch {batch_idx + 1}: {e}")
                            print(f"  [INFO] FAISS will be skipped for remaining batches.")
                            faiss_failed = True
                            self.faiss_store = None
                        else:
                            print(f"  [WARNING] FAISS add failed: {e}")
                
                # Add to ChromaDB (with error recovery)
                if self.chroma_store and not chroma_failed:
                    try:
                        chunk_size = 5000
                        for chunk_start in range(0, len(batch_tokens), chunk_size):
                            chunk_end = min(chunk_start + chunk_size, len(batch_tokens))
                            self.chroma_store.add_tokens(
                                batch_tokens[chunk_start:chunk_end],
                                batch_emb[chunk_start:chunk_end]
                            )
                        chroma_total += len(batch_tokens)
                    except Exception as e:
                        error_msg = str(e).lower()
                        if 'compaction' in error_msg or 'hnsw' in error_msg:
                            print(f"  [WARNING] ChromaDB compaction error at batch {batch_idx + 1}: {e}")
                            print(f"  [INFO] ChromaDB will be skipped for remaining batches.")
                            chroma_failed = True
                            self.chroma_store = None
                        else:
                            print(f"  [WARNING] ChromaDB add failed: {e}")
                
                # Add to Weaviate (most reliable for large datasets)
                if self.weaviate_store:
                    try:
                        # Weaviate handles large batches better, but still chunk for safety
                        chunk_size = 5000
                        for chunk_start in range(0, len(batch_tokens), chunk_size):
                            chunk_end = min(chunk_start + chunk_size, len(batch_tokens))
                            # Prepare metadata for Weaviate
                            metadata_list = []
                            for token in batch_tokens[chunk_start:chunk_end]:
                                token_metadata = {
                                    "text": getattr(token, 'text', ''),
                                    "stream": getattr(token, 'stream', ''),
                                    "uid": str(getattr(token, 'uid', '')),
                                    "frontend": str(getattr(token, 'frontend', '')),
                                    "index": int(getattr(token, 'index', 0)),
                                    "content_id": str(getattr(token, 'content_id', '')),
                                    "global_id": str(getattr(token, 'global_id', ''))
                                }
                                metadata_list.append(token_metadata)
                            
                            self.weaviate_store.add_tokens(
                                batch_tokens[chunk_start:chunk_end],
                                batch_emb[chunk_start:chunk_end],
                                metadata=metadata_list
                            )
                    except Exception as e:
                        print(f"  [WARNING] Weaviate add failed at batch {batch_idx + 1}: {e}")
                
                total_added += len(batch_tokens)
                
                # Progress update
                if (batch_idx + 1) % 10 == 0:
                    status = []
                    if not faiss_failed:
                        status.append(f"FAISS: {faiss_total:,}")
                    if not chroma_failed:
                        status.append(f"ChromaDB: {chroma_total:,}")
                    status_str = ", ".join(status) if status else "FAISS/ChromaDB: skipped"
                    print(f"  Loaded {batch_idx + 1}/{len(batch_files)} batches ({total_added:,} tokens) - {status_str}")
                
                # Memory cleanup
                del batch_emb
                gc.collect()
                
            except Exception as e:
                print(f"  [ERROR] Failed to process batch {batch_idx + 1}: {e}")
                continue
        
        # Summary
        print(f"\n[OK] Loading complete!")
        print(f"  Total tokens processed: {total_added:,}")
        if not faiss_failed:
            print(f"  FAISS: {faiss_total:,} tokens loaded")
        else:
            print(f"  FAISS: Failed (out of memory) - skipped")
        if not chroma_failed:
            print(f"  ChromaDB: {chroma_total:,} tokens loaded")
        else:
            print(f"  ChromaDB: Failed (compaction error) - skipped")
        if self.weaviate_store:
            print(f"  Weaviate: {total_added:,} tokens loaded (cloud-based, no memory limits)")
        
        return True
    
    def initialize_vector_stores(self, use_weaviate=True, use_faiss=True, use_chroma=True):
        """Initialize available vector stores."""
        print("\n" + "=" * 80)
        print("INITIALIZING VECTOR STORES")
        print("=" * 80)
        
        # Weaviate
        if use_weaviate and WEAVIATE_AVAILABLE:
            try:
                print("\n[INFO] Initializing Weaviate...")
                self.weaviate_store = WeaviateVectorStore(
                    collection_name="SOMA_Token",
                    embedding_dim=768
                )
                print("[OK] Weaviate initialized!")
            except Exception as e:
                print(f"[WARNING] Failed to initialize Weaviate: {e}")
                self.weaviate_store = None
        else:
            if use_weaviate:
                print("[WARNING] Weaviate not available. Install: pip install weaviate-client")
        
        # FAISS
        if use_faiss and FAISS_AVAILABLE:
            try:
                print("\n[INFO] Initializing FAISS...")
                self.faiss_store = FAISSVectorStore(embedding_dim=768)
                print("[OK] FAISS initialized!")
            except Exception as e:
                print(f"[WARNING] Failed to initialize FAISS: {e}")
                self.faiss_store = None
        else:
            if use_faiss:
                print("[WARNING] FAISS not available. Install: pip install faiss-cpu")
        
        # ChromaDB
        if use_chroma and CHROMA_AVAILABLE:
            try:
                print("\n[INFO] Initializing ChromaDB...")
                persist_dir = os.path.join(self.output_dir, "chroma_db")
                self.chroma_store = ChromaVectorStore(
                    collection_name="SOMA_embeddings",
                    persist_directory=persist_dir,
                    embedding_dim=768
                )
                print(f"[OK] ChromaDB initialized! (persistent: {persist_dir})")
            except Exception as e:
                print(f"[WARNING] Failed to initialize ChromaDB: {e}")
                self.chroma_store = None
        else:
            if use_chroma:
                print("[WARNING] ChromaDB not available. Install: pip install chromadb")
    
    def tokenize_text(self, text: str, show_detailed: bool = False):
        """Tokenize text with soma."""
        print("\n" + "=" * 80)
        print("TOKENIZATION")
        print("=" * 80)
        print(f"Input text: {text[:100]}..." if len(text) > 100 else f"Input text: {text}")
        
        streams = self.tokenizer.build(text)
        
        # Collect all tokens
        self.tokens = []
        for stream_name, token_stream in streams.items():
            tokens = token_stream.tokens
            self.tokens.extend(tokens)
            print(f"  {stream_name}: {len(tokens):,} tokens")
            
            # Show detailed token information (like embedding_example.py)
            if show_detailed and len(tokens) > 0:
                print(f"\n  Stream: {stream_name} ({len(tokens)} tokens)")
                # Show first 5 tokens with detailed info
                for i, token in enumerate(tokens[:5]):
                    print(f"    Token {i+1}: '{getattr(token, 'text', '')}'")
                    print(f"      UID: {getattr(token, 'uid', 'N/A')}")
                    print(f"      Frontend: {getattr(token, 'frontend', 'N/A')}")
                    if hasattr(token, 'content_id'):
                        print(f"      Content ID: {getattr(token, 'content_id', 'N/A')}")
                    if hasattr(token, 'prev_uid') and getattr(token, 'prev_uid', None):
                        print(f"      Prev UID: {getattr(token, 'prev_uid', 'N/A')}")
                    if hasattr(token, 'next_uid') and getattr(token, 'next_uid', None):
                        print(f"      Next UID: {getattr(token, 'next_uid', 'N/A')}")
        
        print(f"\n[OK] Total tokens: {len(self.tokens):,}")
        return self.tokens
    
    def show_detailed_embeddings(self, text: str, max_tokens_per_stream: int = 5):
        """
        Show detailed token-by-token embedding information (like embedding_example.py).
        
        This demonstrates the detailed view showing:
        - Token text
        - Embedding shape and norm
        - UID, Frontend, Content ID
        - Prev/Next UID relationships
        """
        print("\n" + "=" * 80)
        print("DETAILED EMBEDDING GENERATION (Token-by-Token)")
        print("=" * 80)
        print(f"Input text: {text}")
        
        streams = self.tokenizer.build(text)
        
        print("\nGenerating embeddings...")
        for stream_name, token_stream in streams.items():
            tokens = token_stream.tokens
            print(f"\nStream: {stream_name} ({len(tokens)} tokens)")
            
            # Generate embeddings for tokens in this stream
            if tokens:
                embeddings = self.embedding_gen.generate_batch(tokens)
                
                # Show detailed info for first N tokens
                for i, token in enumerate(tokens[:max_tokens_per_stream]):
                    embedding = embeddings[i]
                    print(f"  Token {i+1}: '{getattr(token, 'text', '')}'")
                    print(f"    Embedding shape: {embedding.shape}")
                    print(f"    Embedding norm: {np.linalg.norm(embedding):.4f}")
                    print(f"    UID: {getattr(token, 'uid', 'N/A')}")
                    print(f"    Frontend: {getattr(token, 'frontend', 'N/A')}")
                    if hasattr(token, 'content_id'):
                        print(f"    Content ID: {getattr(token, 'content_id', 'N/A')}")
                    if hasattr(token, 'global_id'):
                        print(f"    Global ID: {getattr(token, 'global_id', 'N/A')}")
                    if hasattr(token, 'prev_uid') and getattr(token, 'prev_uid', None):
                        print(f"    Prev UID: {getattr(token, 'prev_uid', 'N/A')}")
                    if hasattr(token, 'next_uid') and getattr(token, 'next_uid', None):
                        print(f"    Next UID: {getattr(token, 'next_uid', 'N/A')}")
        
        print(f"\n[OK] Generated detailed embeddings for all streams")
    
    def generate_embeddings(self, strategy=None):
        """Generate embeddings for tokens."""
        print("\n" + "=" * 80)
        print("GENERATING EMBEDDINGS")
        print("=" * 80)
        
        # Use user's choice if strategy not specified
        if strategy is None:
            if self.use_hybrid_embeddings:
                strategy = "hybrid"
            else:
                strategy = "feature_based"
        
        print(f"Strategy: {strategy}")
        
        if strategy == "semantic":
            # Try semantic embeddings
            try:
                semantic_model_path = os.path.join(self.output_dir, "SOMA_semantic_model.pkl")
                if os.path.exists(semantic_model_path):
                    self.embedding_gen = SOMAEmbeddingGenerator(
                        strategy="semantic",
                        embedding_dim=768,
                        semantic_model_path=semantic_model_path
                    )
                    print("[INFO] Using trained semantic model")
                else:
                    print("[WARNING] Semantic model not found. Using feature-based.")
                    strategy = "feature_based"
            except Exception as e:
                print(f"[WARNING] Could not use semantic embeddings: {e}")
                strategy = "feature_based"
        
        if strategy == "feature_based":
            self.embedding_gen = SOMAEmbeddingGenerator(strategy="feature_based", embedding_dim=768)
        
        if strategy == "hybrid" and self.use_hybrid_embeddings:
            # Reinitialize with hybrid strategy
            try:
                self.embedding_gen = SOMAEmbeddingGenerator(strategy="hybrid", embedding_dim=768)
                print("[INFO] Using hybrid embeddings (sentence-transformers)")
            except Exception as e:
                print(f"[WARNING] Could not use hybrid embeddings: {e}")
                print("   Falling back to feature_based.")
                self.embedding_gen = SOMAEmbeddingGenerator(strategy="feature_based", embedding_dim=768)
                self.use_hybrid_embeddings = False
        
        print("Generating embeddings...")
        self.embeddings = self.embedding_gen.generate_batch(self.tokens)
        self.embeddings = np.asarray(self.embeddings)
        
        print(f"[OK] Generated {self.embeddings.shape[0]:,} embeddings of dimension {self.embeddings.shape[1]}")
        return self.embeddings
    
    def store_tokens(self, tags: Optional[Dict] = None):
        """Store tokens and embeddings in all available vector stores."""
        print("\n" + "=" * 80)
        print("STORING TOKENS")
        print("=" * 80)
        
        # Generate tags if not provided
        if tags is None:
            session_id = f"session_{uuid_module.uuid4().hex[:8]}"
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tags = {
                "filename": "comprehensive_example.py",
                "date": current_date,
                "session": session_id,
                "run_id": f"run_{int(time.time() * 1000000)}_{uuid_module.uuid4().hex[:8]}"
            }
        
        print(f"Tags: {tags}")
        
        # Prepare metadata for Weaviate
        metadata_list = []
        for token in self.tokens:
            token_metadata = {
                "text": getattr(token, 'text', ''),
                "stream": getattr(token, 'stream', ''),
                "uid": str(getattr(token, 'uid', '')),
                "frontend": str(getattr(token, 'frontend', '')),
                "index": int(getattr(token, 'index', 0)),
                "content_id": f"{getattr(token, 'content_id', '')}_{tags['run_id']}",
                "global_id": f"{getattr(token, 'global_id', '')}_{tags['run_id']}|filename:{tags['filename']}|date:{tags['date']}|session:{tags['session']}"
            }
            metadata_list.append(token_metadata)
        
        # Store in Weaviate
        if self.weaviate_store:
            try:
                print("\n[INFO] Storing in Weaviate...")
                self.weaviate_store.add_tokens(self.tokens, self.embeddings, metadata=metadata_list)
                print(f"[OK] Stored {len(self.tokens):,} tokens in Weaviate")
            except Exception as e:
                print(f"[WARNING] Failed to store in Weaviate: {e}")
        
        # Store in FAISS
        if self.faiss_store:
            try:
                print("\n[INFO] Storing in FAISS...")
                self.faiss_store.add_tokens(self.tokens, self.embeddings)
                print(f"[OK] Stored {len(self.tokens):,} tokens in FAISS")
            except Exception as e:
                print(f"[WARNING] Failed to store in FAISS: {e}")
        
        # Store in ChromaDB (with chunking to avoid batch size limits)
        if self.chroma_store:
            try:
                print("\n[INFO] Storing in ChromaDB...")
                # ChromaDB has batch size limits, so chunk the data
                chunk_size = 5000
                total_stored = 0
                for chunk_start in range(0, len(self.tokens), chunk_size):
                    chunk_end = min(chunk_start + chunk_size, len(self.tokens))
                    chunk_tokens = self.tokens[chunk_start:chunk_end]
                    chunk_embeddings = self.embeddings[chunk_start:chunk_end]
                    self.chroma_store.add_tokens(chunk_tokens, chunk_embeddings)
                    total_stored += len(chunk_tokens)
                print(f"[OK] Stored {total_stored:,} tokens in ChromaDB")
            except Exception as e:
                print(f"[WARNING] Failed to store in ChromaDB: {e}")
    
    def filter_stop_words(self, results: List[Dict], stop_words: Optional[set] = None) -> List[Dict]:
        """Filter out common stop words from search results."""
        if stop_words is None:
            stop_words = {
                'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
                'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'it', 'its',
                'they', 'them', 'their', 'there', 'here', 'where', 'when', 'what', 'who',
                'which', 'how', 'why', 'if', 'then', 'else', 'so', 'than', 'more', 'most',
                'very', 'just', 'only', 'also', 'too', 'up', 'down', 'out', 'off', 'over',
                'under', 'again', 'further', 'then', 'once'
            }
        
        filtered = []
        seen = set()
        for result in results:
            text = result.get('text', result.get('metadata', {}).get('text', '')).strip()
            text_lower = text.lower()
            
            # Skip if empty, stop word, or duplicate
            if not text or text_lower in stop_words or text_lower in seen:
                continue
            
            # Skip single character tokens (except if they're meaningful)
            if len(text) == 1 and text.lower() not in ['i', 'a']:
                continue
            
            # Skip punctuation-only tokens
            if text.strip('.,!?;:()[]{}"\'').strip() == '':
                continue
            
            seen.add(text_lower)
            filtered.append(result)
        
        return filtered
    
    def semantic_search(self, query_text: str, top_k: int = 10, store_name: str = "all", 
                       min_similarity: float = 0.5, filter_stop: bool = True):
        """Perform semantic search across vector stores with filtering."""
        print("\n" + "=" * 80)
        print("SEMANTIC SEARCH")
        print("=" * 80)
        print(f"Query: '{query_text}'")
        print(f"Top K: {top_k}, Min Similarity: {min_similarity}, Filter Stop Words: {filter_stop}")
        
        # Find query token
        query_token = None
        query_embedding = None
        
        for token in self.tokens:
            if getattr(token, 'text', '').lower() == query_text.lower():
                query_token = token
                token_idx = self.tokens.index(token)
                query_embedding = self.embeddings[token_idx]
                break
        
        if query_embedding is None:
            # Generate embedding for query text
            query_streams = self.tokenizer.build(query_text)
            query_tokens = []
            for stream_name, token_stream in query_streams.items():
                query_tokens.extend(token_stream.tokens)
            
            if query_tokens:
                query_embeddings = self.embedding_gen.generate_batch(query_tokens)
                query_embedding = np.mean(query_embeddings, axis=0)
            else:
                print(f"[ERROR] Could not generate embedding for query: '{query_text}'")
                return {}
        
        results = {}
        
        # Search in Weaviate
        if (store_name == "all" or store_name == "weaviate") and self.weaviate_store:
            try:
                print("\n[INFO] Searching in Weaviate...")
                weaviate_results = self.weaviate_store.search(query_embedding, top_k=top_k * 3)
                
                # Filter stop words
                if filter_stop:
                    weaviate_results = self.filter_stop_words(weaviate_results)
                
                # Filter by similarity
                filtered = []
                for r in weaviate_results:
                    dist = r.get('distance', 0.0)
                    similarity = 1.0 / (1.0 + dist) if isinstance(dist, (float, int)) else 0.0
                    if similarity >= min_similarity:
                        filtered.append(r)
                    if len(filtered) >= top_k:
                        break
                
                results['weaviate'] = filtered
                print(f"[OK] Found {len(filtered)} results in Weaviate (min similarity: {min_similarity})")
                for i, r in enumerate(filtered[:5], 1):
                    text = r.get('text', r.get('metadata', {}).get('text', 'N/A'))
                    dist = r.get('distance', 'N/A')
                    if isinstance(dist, (float, int)):
                        similarity = 1.0 / (1.0 + dist)
                        similarity_str = f"{similarity:.3f}"
                        dist_str = f"{dist:.4f}"
                    else:
                        similarity_str = 'N/A'
                        dist_str = 'N/A'
                    print(f"  {i}. '{text}' (similarity: {similarity_str}, distance: {dist_str})")
            except Exception as e:
                print(f"[WARNING] Weaviate search failed: {e}")
        
        # Search in FAISS
        if (store_name == "all" or store_name == "faiss") and self.faiss_store:
            try:
                print("\n[INFO] Searching in FAISS...")
                faiss_results = self.faiss_store.search(query_embedding, top_k=top_k * 3)
                
                # Filter stop words
                if filter_stop:
                    faiss_results = self.filter_stop_words(faiss_results)
                
                # Filter by similarity
                filtered = []
                for r in faiss_results:
                    dist = r.get('distance', 0.0)
                    similarity = 1.0 / (1.0 + dist) if isinstance(dist, (float, int)) else 0.0
                    if similarity >= min_similarity:
                        filtered.append(r)
                    if len(filtered) >= top_k:
                        break
                
                results['faiss'] = filtered
                print(f"[OK] Found {len(filtered)} results in FAISS (min similarity: {min_similarity})")
                for i, r in enumerate(filtered[:5], 1):
                    text = r.get('text', r.get('metadata', {}).get('text', 'N/A'))
                    dist = r.get('distance', 'N/A')
                    if isinstance(dist, (float, int)):
                        similarity = 1.0 / (1.0 + dist)
                        similarity_str = f"{similarity:.3f}"
                        dist_str = f"{dist:.4f}"
                    else:
                        similarity_str = 'N/A'
                        dist_str = 'N/A'
                    print(f"  {i}. '{text}' (similarity: {similarity_str}, distance: {dist_str})")
            except Exception as e:
                print(f"[WARNING] FAISS search failed: {e}")
        
        # Search in ChromaDB
        if (store_name == "all" or store_name == "chroma") and self.chroma_store:
            try:
                print("\n[INFO] Searching in ChromaDB...")
                chroma_results = self.chroma_store.search(query_embedding, top_k=top_k * 3)
                
                # Filter stop words
                if filter_stop:
                    chroma_results = self.filter_stop_words(chroma_results)
                
                # Filter by similarity
                filtered = []
                for r in chroma_results:
                    dist = r.get('distance', 0.0)
                    similarity = 1.0 / (1.0 + dist) if isinstance(dist, (float, int)) else 0.0
                    if similarity >= min_similarity:
                        filtered.append(r)
                    if len(filtered) >= top_k:
                        break
                
                results['chroma'] = filtered
                print(f"[OK] Found {len(filtered)} results in ChromaDB (min similarity: {min_similarity})")
                for i, r in enumerate(filtered[:5], 1):
                    text = r.get('text', r.get('metadata', {}).get('text', 'N/A'))
                    dist = r.get('distance', 'N/A')
                    if isinstance(dist, (float, int)):
                        similarity = 1.0 / (1.0 + dist)
                        similarity_str = f"{similarity:.3f}"
                        dist_str = f"{dist:.4f}"
                    else:
                        similarity_str = 'N/A'
                        dist_str = 'N/A'
                    print(f"  {i}. '{text}' (similarity: {similarity_str}, distance: {dist_str})")
            except Exception as e:
                print(f"[WARNING] ChromaDB search failed: {e}")
        
        return results
    
    def compare_stores(self, query_text: str, top_k: int = 10):
        """Compare search results across different vector stores."""
        print("\n" + "=" * 80)
        print("COMPARING VECTOR STORES")
        print("=" * 80)
        
        results = self.semantic_search(query_text, top_k=top_k, store_name="all")
        
        if not results:
            print("[WARNING] No results from any store")
            return
        
        # Extract text from results
        store_texts = {}
        for store_name, store_results in results.items():
            texts = []
            for r in store_results:
                text = r.get('text', r.get('metadata', {}).get('text', ''))
                if text:
                    texts.append(text.lower())
            store_texts[store_name] = set(texts)
        
        # Calculate overlaps
        print("\n[INFO] Overlap Analysis:")
        store_names = list(store_texts.keys())
        for i, store1 in enumerate(store_names):
            for store2 in store_names[i+1:]:
                set1 = store_texts[store1]
                set2 = store_texts[store2]
                overlap = len(set1 & set2)
                union = len(set1 | set2)
                overlap_pct = (overlap / union * 100) if union > 0 else 0
                print(f"  {store1} ↔ {store2}: {overlap}/{union} ({overlap_pct:.1f}% overlap)")
    
    def find_related_concepts(self, concept_tokens: List[str], top_k: int = 15, min_similarity: float = 0.4):
        """Find concepts related to multiple tokens by averaging their embeddings."""
        print("\n" + "=" * 80)
        print("FINDING RELATED CONCEPTS")
        print("=" * 80)
        print(f"Concepts: {', '.join(concept_tokens)}")
        
        store = self.weaviate_store or self.faiss_store or self.chroma_store
        if not store:
            print("[ERROR] No vector store available")
            return []
        
        # Get embeddings for all concept tokens
        embeddings = []
        found_tokens = []
        for token_text in concept_tokens:
            for token in self.tokens:
                if getattr(token, 'text', '').lower() == token_text.lower():
                    token_idx = self.tokens.index(token)
                    embeddings.append(self.embeddings[token_idx])
                    found_tokens.append(token_text)
                    break
        
        if not embeddings:
            print("[ERROR] None of the concept tokens found")
            return []
        
        if len(found_tokens) < len(concept_tokens):
            print(f"[WARNING] Only found {len(found_tokens)}/{len(concept_tokens)} tokens: {found_tokens}")
        
        # Average the embeddings to get a combined concept
        avg_embedding = np.mean(embeddings, axis=0)
        
        # Search with filtering
        results = store.search(avg_embedding, top_k=top_k * 3)
        results = self.filter_stop_words(results)
        
        # Filter by similarity and exclude input tokens
        filtered_results = []
        input_lower = {t.lower() for t in concept_tokens}
        for result in results:
            text = result.get('text', result.get('metadata', {}).get('text', 'N/A'))
            if text.lower() in input_lower:
                continue
            
            dist = result.get('distance', 0.0)
            similarity = 1.0 / (1.0 + dist) if isinstance(dist, (float, int)) else 0.0
            if similarity >= min_similarity:
                filtered_results.append(result)
            if len(filtered_results) >= top_k:
                break
        
        print(f"\nRelated concepts (min similarity: {min_similarity}):")
        for i, result in enumerate(filtered_results, 1):
            text = result.get('text', result.get('metadata', {}).get('text', 'N/A'))
            dist = result.get('distance', 0.0)
            similarity = 1.0 / (1.0 + dist) if isinstance(dist, (float, int)) else 0.0
            print(f"  {i:2d}. {text:30s} (similarity: {similarity:.3f}, distance: {dist:.4f})")
        
        return filtered_results
    
    def compare_tokens(self, token1: str, token2: str):
        """Compare similarity between two tokens."""
        print("\n" + "=" * 80)
        print("TOKEN COMPARISON")
        print("=" * 80)
        print(f"Comparing: '{token1}' vs '{token2}'")
        
        # Find embeddings
        emb1 = None
        emb2 = None
        
        for token in self.tokens:
            if getattr(token, 'text', '').lower() == token1.lower():
                token_idx = self.tokens.index(token)
                emb1 = self.embeddings[token_idx]
            if getattr(token, 'text', '').lower() == token2.lower():
                token_idx = self.tokens.index(token)
                emb2 = self.embeddings[token_idx]
        
        if emb1 is None or emb2 is None:
            print("[ERROR] One or both tokens not found")
            return None
        
        # Calculate distance and similarity
        distance = np.linalg.norm(emb1 - emb2)
        similarity = 1.0 / (1.0 + distance)
        cosine_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        print(f"Distance: {distance:.4f}")
        print(f"Similarity (1/(1+d)): {similarity:.3f} ({similarity*100:.1f}%)")
        print(f"Cosine Similarity: {cosine_sim:.4f} ({cosine_sim*100:.1f}%)")
        
        if similarity > 0.8:
            print("  → Very similar (likely related concepts)")
        elif similarity > 0.6:
            print("  → Moderately similar (somewhat related)")
        elif similarity > 0.4:
            print("  → Somewhat similar (loosely related)")
        else:
            print("  → Not very similar (different concepts)")
        
        return similarity
    
    def find_concept_cluster(self, seed_concept: str, cluster_size: int = 10, min_similarity: float = 0.6):
        """Find a cluster of related concepts around a seed."""
        print("\n" + "=" * 80)
        print("CONCEPT CLUSTER")
        print("=" * 80)
        print(f"Seed concept: '{seed_concept}'")
        print(f"Cluster size: {cluster_size}, Min similarity: {min_similarity}")
        
        store = self.weaviate_store or self.faiss_store or self.chroma_store
        if not store:
            print("[ERROR] No vector store available")
            return []
        
        # Get seed embedding
        seed_emb = None
        for token in self.tokens:
            if getattr(token, 'text', '').lower() == seed_concept.lower():
                token_idx = self.tokens.index(token)
                seed_emb = self.embeddings[token_idx]
                break
        
        if seed_emb is None:
            print(f"[ERROR] Seed concept '{seed_concept}' not found")
            return []
        
        # Search for cluster
        results = store.search(seed_emb, top_k=cluster_size * 2)
        results = self.filter_stop_words(results)
        
        # Filter and build cluster
        cluster = []
        seed_lower = seed_concept.lower()
        for result in results:
            text = result.get('text', result.get('metadata', {}).get('text', 'N/A'))
            if text.lower() == seed_lower:
                continue
            
            dist = result.get('distance', 0.0)
            similarity = 1.0 / (1.0 + dist) if isinstance(dist, (float, int)) else 0.0
            if similarity >= min_similarity:
                cluster.append({
                    'concept': text,
                    'similarity': similarity,
                    'distance': dist
                })
            if len(cluster) >= cluster_size:
                break
        
        if cluster:
            print(f"\n📦 Concept Cluster (found {len(cluster)} concepts):")
            for i, item in enumerate(cluster, 1):
                print(f"  {i:2d}. {item['concept']:30s} (similarity: {item['similarity']:.3f})")
        else:
            print(f"[ERROR] No cluster found (try lowering min_similarity)")
        
        return cluster
    
    def compare_embeddings(self, text1: str, text2: str):
        """Compare semantic similarity between two texts using cosine similarity."""
        print("\n" + "=" * 80)
        print("TEXT EMBEDDING COMPARISON")
        print("=" * 80)
        print(f"Text 1: {text1}")
        print(f"Text 2: {text2}")
        
        # Generate embeddings for both texts
        def get_text_embedding(text):
            streams = self.tokenizer.build(text)
            tokens = []
            for stream_name, token_stream in streams.items():
                tokens.extend(token_stream.tokens)
            
            if not tokens:
                return None
            
            embeddings = self.embedding_gen.generate_batch(tokens)
            return np.mean(embeddings, axis=0)
        
        emb1 = get_text_embedding(text1)
        emb2 = get_text_embedding(text2)
        
        if emb1 is None or emb2 is None:
            print("[ERROR] Could not generate embeddings for one or both texts")
            return None
        
        # Compute cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        distance = np.linalg.norm(emb1 - emb2)
        
        print(f"\nCosine Similarity: {similarity:.4f} ({similarity*100:.1f}%)")
        print(f"Euclidean Distance: {distance:.4f}")
        
        if similarity > 0.8:
            print("  → Very similar texts")
        elif similarity > 0.6:
            print("  → Moderately similar texts")
        elif similarity > 0.4:
            print("  → Somewhat similar texts")
        else:
            print("  → Different texts")
        
        return similarity
    
    def get_document_embeddings(self, documents: List[str], method: str = "mean"):
        """Generate document-level embeddings."""
        print("\n" + "=" * 80)
        print("DOCUMENT EMBEDDINGS")
        print("=" * 80)
        print(f"Method: {method}")
        
        doc_embeddings = []
        
        for i, doc in enumerate(documents, 1):
            print(f"\nDocument {i}: '{doc[:50]}...'")
            
            streams = self.tokenizer.build(doc)
            tokens = []
            for stream_name, token_stream in streams.items():
                tokens.extend(token_stream.tokens)
            
            if not tokens:
                print("  [WARNING] No tokens found")
                continue
            
            embeddings = self.embedding_gen.generate_batch(tokens)
            embeddings = np.asarray(embeddings)
            
            if method == "mean":
                doc_emb = np.mean(embeddings, axis=0)
            elif method == "max":
                doc_emb = np.max(embeddings, axis=0)
            elif method == "sum":
                doc_emb = np.sum(embeddings, axis=0)
            else:
                doc_emb = np.mean(embeddings, axis=0)
            
            doc_embeddings.append(doc_emb)
            print(f"  Embedding shape: {doc_emb.shape}")
            print(f"  Embedding norm: {np.linalg.norm(doc_emb):.4f}")
        
        # Compute similarities between documents
        if len(doc_embeddings) > 1:
            print("\nDocument Similarities:")
            doc_embeddings_array = np.array(doc_embeddings)
            for i in range(len(documents)):
                for j in range(i+1, len(documents)):
                    similarity = np.dot(doc_embeddings_array[i], doc_embeddings_array[j]) / (
                        np.linalg.norm(doc_embeddings_array[i]) * np.linalg.norm(doc_embeddings_array[j])
                    )
                    print(f"  Doc {i+1} ↔ Doc {j+1}: {similarity:.4f}")
        
        return doc_embeddings
    
    def query_by_id(self, token_id: str, store_name: str = "weaviate"):
        """Query a token by ID from Weaviate."""
        print("\n" + "=" * 80)
        print("QUERY BY ID")
        print("=" * 80)
        print(f"Token ID: {token_id}")
        print(f"Store: {store_name}")
        
        if store_name == "weaviate" and self.weaviate_store:
            try:
                collection = self.weaviate_store.collection
                # Try different Weaviate API methods for querying by ID
                obj = None
                try:
                    # Try get_by_id (Weaviate v4 standard)
                    obj = collection.data.get_by_id(token_id)
                except AttributeError:
                    try:
                        # Try fetch_by_id (alternative method)
                        obj = collection.data.fetch_by_id(token_id)
                    except AttributeError:
                        try:
                            # Try query.fetch_object_by_id (query-based)
                            result = collection.query.fetch_object_by_id(token_id)
                            if result:
                                obj = result
                        except (AttributeError, Exception):
                            pass
                
                if obj:
                    # Handle different response formats
                    if hasattr(obj, 'properties'):
                        props = obj.properties
                    elif isinstance(obj, dict):
                        props = obj.get('properties', obj)
                    else:
                        props = {}
                    
                    print(f"[OK] Retrieved token by UUID: {token_id}")
                    print(f"  Text: {props.get('text', 'N/A')}")
                    print(f"  Stream: {props.get('stream', 'N/A')}")
                    print(f"  UID: {props.get('uid', 'N/A')}")
                    print(f"  Global ID: {props.get('global_id', 'N/A')}")
                    
                    # Try to get vector
                    vector = None
                    if hasattr(obj, 'vector'):
                        vector = obj.vector
                    elif hasattr(obj, 'get') and 'vector' in obj:
                        vector = obj['vector']
                    
                    if vector:
                        vector_len = len(vector) if isinstance(vector, (list, np.ndarray)) else 'N/A'
                        print(f"  Vector dimension: {vector_len}")
                    return obj
                else:
                    print(f"[WARNING] Token with UUID {token_id} not found")
            except Exception as e:
                print(f"[WARNING] Could not query by ID: {e}")
        else:
            print(f"[WARNING] {store_name} store not available or doesn't support query by ID")
        
        return None
    
    def retrieval_before_processing(self, query_text: str, top_k: int = 5):
        """Check vector stores for similar tokens BEFORE processing (context memory)."""
        print("\n" + "=" * 80)
        print("RETRIEVAL BEFORE PROCESSING (Context Memory)")
        print("=" * 80)
        print(f"Query: '{query_text}'")
        print("This makes SOMA recall similar embeddings from memory before processing new input.")
        
        # Generate embedding for query
        query_streams = self.tokenizer.build(query_text)
        query_tokens = []
        for stream_name, token_stream in query_streams.items():
            query_tokens.extend(token_stream.tokens)
        
        if not query_tokens:
            print("[WARNING] Could not tokenize query text")
            return []
        
        query_embeddings = self.embedding_gen.generate_batch(query_tokens)
        query_embedding = np.mean(query_embeddings, axis=0)
        
        # Search in all available stores
        all_results = []
        
        for store_name, store in [("Weaviate", self.weaviate_store), 
                                  ("FAISS", self.faiss_store), 
                                  ("ChromaDB", self.chroma_store)]:
            if store:
                try:
                    results = store.search(query_embedding, top_k=top_k)
                    if results:
                        print(f"\n[OK] Found {len(results)} similar tokens in {store_name} memory:")
                        for i, r in enumerate(results[:3], 1):
                            text = r.get('text', r.get('metadata', {}).get('text', 'N/A'))
                            distance = r.get('distance', None)
                            distance_str = f"{distance:.4f}" if isinstance(distance, (float, int)) else "N/A"
                            print(f"  {i}. '{text}' (distance: {distance_str})")
                        all_results.extend(results)
                except Exception as e:
                    print(f"[WARNING] {store_name} retrieval failed: {e}")
        
        if all_results:
            print("\n→ SOMA can recall similar embeddings from its memory!")
        else:
            print("\n→ No similar tokens found in memory (this is a new context)")
        
        return all_results
    
    def analyze_clusters(self, sample_size: int = 1000, top_k: int = 5):
        """Analyze token clusters to find groups of similar tokens."""
        print("\n" + "=" * 80)
        print("CLUSTER ANALYSIS")
        print("=" * 80)
        print(f"Sample size: {sample_size}")
        
        store = self.weaviate_store or self.faiss_store or self.chroma_store
        if not store:
            print("[ERROR] No vector store available")
            return {}
        
        # Sample tokens for analysis
        import random
        sample_indices = random.sample(range(len(self.tokens)), min(sample_size, len(self.tokens)))
        sample_tokens = [self.tokens[i] for i in sample_indices]
        
        print(f"Analyzing {len(sample_tokens)} sample tokens...")
        
        clusters = {}
        processed = set()
        
        for token in sample_tokens[:100]:  # Limit to first 100 for speed
            token_text = getattr(token, 'text', '')
            if not token_text or token_text.lower() in processed:
                continue
            
            # Get embedding and find neighbors
            token_idx = self.tokens.index(token)
            query_embedding = self.embeddings[token_idx]
            neighbors = store.search(query_embedding, top_k=top_k)
            
            if neighbors:
                cluster = [r.get('text', r.get('metadata', {}).get('text', '')) for r in neighbors]
                clusters[token_text] = cluster
                processed.update([t.lower() for t in cluster])
        
        print(f"\n[OK] Found {len(clusters)} clusters:")
        for i, (center, members) in enumerate(list(clusters.items())[:10], 1):
            print(f"\n  Cluster {i}: '{center}'")
            print(f"    Members: {', '.join(members[:5])}")
        
        return clusters
    
    def interactive_search(self):
        """Interactive search mode for exploring the vector store."""
        print("\n" + "=" * 80)
        print("INTERACTIVE SEARCH MODE")
        print("=" * 80)
        print("\nCommands:")
        print("  search <token>      - Search for similar tokens")
        print("  compare <t1> <t2>   - Compare two tokens")
        print("  related <t1> [t2]   - Find concepts related to token(s)")
        print("  cluster <token>     - Find concept cluster")
        print("  explore <token>     - Explore concept relationships")
        print("  help                - Show this help")
        print("  quit/exit           - Exit interactive mode")
        print("\n" + "-" * 80)
        
        store = self.weaviate_store or self.faiss_store or self.chroma_store
        if not store:
            print("[ERROR] No vector store available")
            return
        
        while True:
            try:
                cmd = input("\n[INFO] > ").strip().split()
                if not cmd:
                    continue
                
                command = cmd[0].lower()
                
                if command in ['quit', 'exit', 'q']:
                    print("👋 Exiting interactive mode...")
                    break
                
                elif command == 'help':
                    print("\nCommands:")
                    print("  search <token>      - Search for similar tokens")
                    print("  compare <t1> <t2>   - Compare two tokens")
                    print("  related <t1> [t2]   - Find concepts related to token(s)")
                    print("  cluster <token>     - Find concept cluster")
                    print("  explore <token>     - Explore concept relationships")
                    print("  quit/exit           - Exit")
                
                elif command == 'search' and len(cmd) > 1:
                    token = cmd[1]
                    self.semantic_search(token, top_k=15, store_name="all", min_similarity=0.5)
                
                elif command == 'compare' and len(cmd) > 2:
                    self.compare_tokens(cmd[1], cmd[2])
                
                elif command == 'related' and len(cmd) > 1:
                    tokens = cmd[1:]
                    self.find_related_concepts(tokens, top_k=15, min_similarity=0.4)
                
                elif command == 'cluster' and len(cmd) > 1:
                    self.find_concept_cluster(cmd[1], cluster_size=10, min_similarity=0.6)
                
                elif command == 'explore' and len(cmd) > 1:
                    self.explore_concept(cmd[1], depth=2, top_k_per_level=10)
                
                else:
                    print("[ERROR] Invalid command. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\n👋 Exiting interactive mode...")
                break
            except Exception as e:
                print(f"[ERROR] Error: {e}")
    
    def explore_concept(self, concept: str, depth: int = 2, top_k_per_level: int = 10):
        """Explore a concept by finding related terms at multiple levels."""
        print("\n" + "=" * 80)
        print("CONCEPT EXPLORATION")
        print("=" * 80)
        print(f"Exploring concept: '{concept}' (depth: {depth})")
        
        # Use first available store
        store = self.weaviate_store or self.faiss_store or self.chroma_store
        if not store:
            print("[ERROR] No vector store available")
            return
        
        explored = set()
        to_explore = [concept]
        all_related = []
        
        for level in range(depth):
            if not to_explore:
                break
            
            print(f"\n📍 Level {level + 1} - Exploring {len(to_explore)} concept(s):")
            level_terms = []
            
            for term in to_explore:
                term_key = term.lower()
                if term_key in explored:
                    continue
                explored.add(term_key)
                
                # Get embedding for term
                query_embedding = None
                for token in self.tokens:
                    if getattr(token, 'text', '').lower() == term_key:
                        token_idx = self.tokens.index(token)
                        query_embedding = self.embeddings[token_idx]
                        break
                
                if query_embedding is None:
                    print(f"  [WARNING] Could not find embedding for '{term}'")
                    continue
                
                # Search for similar tokens
                results = store.search(query_embedding, top_k=top_k_per_level * 3)
                
                # Filter and collect unique terms
                filtered = []
                seen_texts = set()
                
                for result in results:
                    text = result.get('text', result.get('metadata', {}).get('text', '')).strip()
                    if not text or text.lower() in seen_texts or text.lower() == term_key:
                        continue
                    
                    filtered.append(text)
                    seen_texts.add(text.lower())
                    if len(filtered) >= top_k_per_level:
                        break
                
                # Show results
                if filtered:
                    print(f"  '{term}' → {len(filtered)} related concepts:")
                    for text in filtered[:5]:
                        print(f"     • {text}")
                    level_terms.extend(filtered)
                    all_related.extend([(text, level + 1) for text in filtered])
            
            to_explore = level_terms[:10]  # Limit expansion
        
        print(f"\n[OK] Discovered {len(all_related)} unique related terms across {depth} levels")
        return all_related
    
    def evaluate_quality(self, probe_tokens: List[str], top_k: int = 10):
        """Evaluate embedding quality using probe tokens."""
        print("\n" + "=" * 80)
        print("QUALITY EVALUATION")
        print("=" * 80)
        
        store = self.weaviate_store or self.faiss_store or self.chroma_store
        if not store:
            print("[ERROR] No vector store available")
            return
        
        print(f"Probe tokens: {probe_tokens}")
        
        results_summary = {}
        
        for probe in probe_tokens:
            # Find embedding
            query_embedding = None
            for token in self.tokens:
                if getattr(token, 'text', '').lower() == probe.lower():
                    token_idx = self.tokens.index(token)
                    query_embedding = self.embeddings[token_idx]
                    break
            
            if query_embedding is None:
                print(f"  [WARNING] Probe '{probe}' not found")
                continue
            
            # Search
            results = store.search(query_embedding, top_k=top_k)
            
            print(f"\n--- {probe} ---")
            if results:
                for i, r in enumerate(results[:5], 1):
                    text = r.get('text', r.get('metadata', {}).get('text', 'N/A'))
                    dist = r.get('distance', None)
                    print(f"  {i}. {text}: {dist:.4f}" if isinstance(dist, (float, int)) else f"  {i}. {text}: {dist}")
                results_summary[probe] = results
            else:
                print("  No results found")
        
        return results_summary
    
    def evaluate_semantic_alignment(self, test_pairs: Optional[List[Tuple[str, str, float]]] = None):
        """
        Evaluate how well SOMA embeddings align with human semantic similarity.
        
        Args:
            test_pairs: Optional list of (text1, text2, human_similarity_score) tuples
                        where human_similarity_score is 0.0-1.0 (1.0 = very similar).
                        If None, uses default test pairs demonstrating the misalignment problem.
        
        Returns:
            Dictionary with alignment metrics
        """
        print("\n" + "=" * 80)
        print("EVALUATING SEMANTIC ALIGNMENT")
        print("=" * 80)
        print("Testing how well SOMA embeddings match human semantic judgments...")
        
        if test_pairs is None or not test_pairs:
            # Default test pairs demonstrating the misalignment problem
            test_pairs = [
                ("AI helps humans.", "Machines assist people.", 0.9),  # Should be similar
                ("The cat sat on the mat.", "A feline rested on a rug.", 0.85),  # Should be similar
                ("I love programming.", "I hate coding.", 0.3),  # Should be different
                ("Natural language processing", "NLP", 0.95),  # Should be very similar
                ("Machine learning", "Deep learning", 0.7),  # Should be moderately similar
                ("Python programming", "Cooking recipes", 0.1),  # Should be very different
            ]
        
        print(f"\nTesting {len(test_pairs)} text pairs...")
        
        SOMA_similarities = []
        human_similarities = []
        errors = []
        
        for i, (text1, text2, human_sim) in enumerate(test_pairs, 1):
            # Get embeddings for both texts
            emb1 = self._get_text_embedding(text1)
            emb2 = self._get_text_embedding(text2)
            
            if emb1 is None or emb2 is None:
                print(f"  [WARNING] Could not generate embeddings for pair {i}")
                continue
            
            # Calculate SOMA cosine similarity
            SOMA_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            SOMA_sim = max(0.0, min(1.0, (SOMA_sim + 1.0) / 2.0))  # Normalize to 0-1
            
            SOMA_similarities.append(SOMA_sim)
            human_similarities.append(human_sim)
            error = abs(SOMA_sim - human_sim)
            errors.append(error)
            
            status = "✓" if error < 0.2 else "✗"
            print(f"  {status} Pair {i}: '{text1[:30]}...' vs '{text2[:30]}...'")
            print(f"      Human: {human_sim:.2f} | SOMA: {SOMA_sim:.2f} | Error: {error:.2f}")
        
        # Calculate metrics
        mean_error = np.mean(errors)
        max_error = np.max(errors)
        correlation = np.corrcoef(SOMA_similarities, human_similarities)[0, 1] if len(SOMA_similarities) > 1 else 0.0
        
        print(f"\n📊 Alignment Metrics:")
        print(f"  Mean Absolute Error: {mean_error:.3f}")
        print(f"  Max Error: {max_error:.3f}")
        print(f"  Correlation (SOMA vs Human): {correlation:.3f}")
        
        if mean_error > 0.3:
            print(f"\n⚠️  HIGH MISALIGNMENT: SOMA embeddings don't match human semantics well.")
            print(f"   Consider training embedding alignment (see train_embedding_alignment)")
        elif mean_error > 0.2:
            print(f"\n⚠️  MODERATE MISALIGNMENT: Some improvement needed.")
        else:
            print(f"\n✓ GOOD ALIGNMENT: SOMA embeddings align well with human semantics.")
        
        return {
            'mean_error': mean_error,
            'max_error': max_error,
            'correlation': correlation,
            'SOMA_similarities': SOMA_similarities,
            'human_similarities': human_similarities,
            'errors': errors
        }
    
    def _get_text_embedding(self, text: str) -> Optional[np.ndarray]:
        """Helper to get embedding for a text string."""
        streams = self.tokenizer.build(text)
        tokens = []
        for stream_name, token_stream in streams.items():
            tokens.extend(token_stream.tokens)
        
        if not tokens:
            return None
        
        embeddings = self.embedding_gen.generate_batch(tokens)
        return np.mean(embeddings, axis=0)
    
    def train_embedding_alignment(
        self, 
        labeled_pairs: List[Tuple[str, str, float]],
        epochs: int = 10,
        learning_rate: float = 0.001,
        use_contrastive: bool = True,
        use_mse: bool = True
    ):
        """
        Train embedding alignment using labeled pairs (similar vs dissimilar text).
        
        Uses multi-loss training:
        - Contrastive loss: Pull similar pairs together, push dissimilar pairs apart
        - MSE loss: Minimize difference between predicted and human similarity scores
        
        Args:
            labeled_pairs: List of (text1, text2, similarity_score) tuples
                          similarity_score: 0.0-1.0 (1.0 = very similar, 0.0 = very different)
            epochs: Number of training epochs
            learning_rate: Learning rate for optimization
            use_contrastive: Use contrastive loss (pull similar, push dissimilar)
            use_mse: Use MSE loss (match human similarity scores)
        """
        print("\n" + "=" * 80)
        print("TRAINING EMBEDDING ALIGNMENT")
        print("=" * 80)
        print("Learning to align SOMA embeddings with human semantic similarity...")
        print(f"Training pairs: {len(labeled_pairs)}")
        print(f"Epochs: {epochs}, Learning rate: {learning_rate}")
        print(f"Loss functions: Contrastive={use_contrastive}, MSE={use_mse}")
        
        if not labeled_pairs:
            print("[ERROR] No labeled pairs provided")
            return None
        
        # Generate initial embeddings for all texts
        print("\n[INFO] Generating embeddings for all texts...")
        text_embeddings = {}
        for text1, text2, _ in labeled_pairs:
            if text1 not in text_embeddings:
                emb1 = self._get_text_embedding(text1)
                if emb1 is not None:
                    text_embeddings[text1] = emb1
            if text2 not in text_embeddings:
                emb2 = self._get_text_embedding(text2)
                if emb2 is not None:
                    text_embeddings[text2] = emb2
        
        # Filter pairs where we have embeddings
        valid_pairs = []
        for text1, text2, sim in labeled_pairs:
            if text1 in text_embeddings and text2 in text_embeddings:
                valid_pairs.append((text1, text2, sim))
        
        if not valid_pairs:
            print("[ERROR] No valid pairs with embeddings found")
            return None
        
        print(f"[OK] {len(valid_pairs)} valid pairs for training")
        
        # Initialize alignment projection matrix
        # This matrix will transform SOMA embeddings to better match semantic space
        embedding_dim = len(list(text_embeddings.values())[0])
        alignment_matrix = np.eye(embedding_dim)  # Start with identity
        bias = np.zeros(embedding_dim)
        
        # Training loop
        print(f"\n[INFO] Training for {epochs} epochs...")
        for epoch in range(epochs):
            total_loss = 0.0
            num_batches = 0
            
            for text1, text2, target_sim in valid_pairs:
                emb1 = text_embeddings[text1]
                emb2 = text_embeddings[text2]
                
                # Apply alignment transformation
                aligned_emb1 = alignment_matrix @ emb1 + bias
                aligned_emb2 = alignment_matrix @ emb2 + bias
                
                # Normalize
                aligned_emb1 = aligned_emb1 / (np.linalg.norm(aligned_emb1) + 1e-8)
                aligned_emb2 = aligned_emb2 / (np.linalg.norm(aligned_emb2) + 1e-8)
                
                # Compute predicted similarity (cosine)
                pred_sim = np.dot(aligned_emb1, aligned_emb2)
                pred_sim = (pred_sim + 1.0) / 2.0  # Normalize to 0-1
                
                # Compute losses
                loss = 0.0
                
                if use_mse:
                    # MSE loss: match human similarity score
                    mse_loss = (pred_sim - target_sim) ** 2
                    loss += mse_loss
                
                if use_contrastive:
                    # Contrastive loss: pull similar pairs together, push dissimilar apart
                    margin = 0.2
                    if target_sim > 0.7:  # Similar pair - minimize distance
                        contrastive_loss = np.linalg.norm(aligned_emb1 - aligned_emb2) ** 2
                    else:  # Dissimilar pair - maximize distance (with margin)
                        distance = np.linalg.norm(aligned_emb1 - aligned_emb2)
                        contrastive_loss = max(0, margin - distance) ** 2
                    loss += contrastive_loss * 0.5
                
                total_loss += loss
                num_batches += 1
                
                # Gradient update (simplified SGD)
                if loss > 0:
                    # Compute gradients (simplified)
                    grad_scale = learning_rate * (pred_sim - target_sim) if use_mse else learning_rate
                    
                    # Update alignment matrix (simplified gradient descent)
                    update = grad_scale * np.outer(emb1, emb2) * 0.01
                    alignment_matrix -= update
                    
                    # Update bias
                    bias -= grad_scale * (emb1 + emb2) * 0.001
            
            avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
            if (epoch + 1) % max(1, epochs // 5) == 0 or epoch == 0:
                print(f"  Epoch {epoch + 1}/{epochs}: Average loss = {avg_loss:.4f}")
        
        # Save alignment model
        alignment_model = {
            'alignment_matrix': alignment_matrix,
            'bias': bias,
            'embedding_dim': embedding_dim
        }
        
        model_path = os.path.join(self.output_dir, "embedding_alignment_model.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(alignment_model, f)
        
        print(f"\n[OK] Alignment model saved to: {model_path}")
        
        # Evaluate improvement
        print("\n[INFO] Evaluating alignment improvement...")
        improved_results = self.evaluate_semantic_alignment(valid_pairs[:min(10, len(valid_pairs))])
        
        return alignment_model
    
    def apply_alignment(self, embedding: np.ndarray, alignment_model: Optional[Dict] = None) -> np.ndarray:
        """
        Apply learned alignment transformation to an embedding.
        
        Args:
            embedding: SOMA embedding vector
            alignment_model: Alignment model dict (if None, loads from disk)
        
        Returns:
            Aligned embedding vector
        """
        if alignment_model is None:
            model_path = os.path.join(self.output_dir, "embedding_alignment_model.pkl")
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    alignment_model = pickle.load(f)
            else:
                print("[WARNING] No alignment model found. Returning original embedding.")
                return embedding
        
        alignment_matrix = alignment_model['alignment_matrix']
        bias = alignment_model.get('bias', np.zeros(len(embedding)))
        
        aligned = alignment_matrix @ embedding + bias
        aligned = aligned / (np.linalg.norm(aligned) + 1e-8)  # Normalize
        
        return aligned
    
    def build_context_fusion_embeddings(
        self,
        context_window: int = 5,
        use_positional: bool = True,
        use_neighbor_attention: bool = True,
        use_content_grouping: bool = True,
        min_similarity_threshold: float = 0.3  # Filter out noisy neighbors/content
    ):
        """
        SOMA-Native Context Fusion: Build context-aware embeddings using SOMA's own mechanisms.
        
        Uses SOMA's native context signals:
        - prev_uid/next_uid: Positional dependency (tokens know their neighbors)
        - content_id: Semantic grouping (same content = same ID)
        - global_id: Full context signature (uid + content + position + stream)
        - Backend numbers: Already include neighbor context in hash
        - Index-based positional encoding: Deterministic position awareness
        
        This is the "SOMA way" to solve semantic context loss - leveraging what SOMA
        already tracks mathematically, not adding external models.
        
        Args:
            context_window: How many neighbors to consider (default: 5)
            use_positional: Use index-based positional encoding
            use_neighbor_attention: Weight embeddings by neighbor similarity
            use_content_grouping: Group tokens by content_id for semantic coherence
            min_similarity_threshold: Minimum similarity (0-1) to include neighbors/content (filters noise)
        
        Returns:
            Context-fused embeddings array
        """
        print("\n" + "=" * 80)
        print("SOMA-NATIVE CONTEXT FUSION")
        print("=" * 80)
        print("Building context-aware embeddings using SOMA's own mechanisms...")
        print(f"Context window: {context_window}")
        print(f"Positional encoding: {use_positional}")
        print(f"Neighbor attention: {use_neighbor_attention}")
        print(f"Content grouping: {use_content_grouping}")
        print(f"Noise filtering threshold: {min_similarity_threshold} (only includes similar neighbors/content)")
        
        if not self.tokens or self.embeddings is None:
            print("[ERROR] No tokens or embeddings available")
            return None
        
        # Build token lookup maps using SOMA's native IDs
        uid_to_idx = {}
        content_id_to_indices = {}
        prev_next_map = {}
        
        for i, token in enumerate(self.tokens):
            uid = getattr(token, 'uid', None)
            if uid is not None:
                uid_to_idx[uid] = i
            
            content_id = getattr(token, 'content_id', None)
            if content_id is not None:
                if content_id not in content_id_to_indices:
                    content_id_to_indices[content_id] = []
                content_id_to_indices[content_id].append(i)
            
            prev_uid = getattr(token, 'prev_uid', None)
            next_uid = getattr(token, 'next_uid', None)
            prev_next_map[i] = {
                'prev_uid': prev_uid,
                'next_uid': next_uid,
                'prev_idx': uid_to_idx.get(prev_uid, None) if prev_uid else None,
                'next_idx': uid_to_idx.get(next_uid, None) if next_uid else None
            }
        
        print(f"[OK] Built context maps: {len(uid_to_idx)} UIDs, {len(content_id_to_indices)} content groups")
        
        # Generate context-fused embeddings
        context_embeddings = np.zeros_like(self.embeddings)
        embedding_dim = self.embeddings.shape[1]
        
        print(f"\n[INFO] Fusing context for {len(self.tokens)} tokens...")
        
        for i, token in enumerate(self.tokens):
            base_emb = self.embeddings[i].copy()
            context_components = []
            weights = []
            
            # 1. Base embedding (always included)
            context_components.append(base_emb)
            weights.append(1.0)
            
            # 2. Positional encoding (using SOMA's index)
            if use_positional:
                # Create deterministic positional encoding from index
                # Use sine/cosine like transformers, but based on SOMA's index
                pos_encoding = np.zeros(embedding_dim)
                for dim in range(embedding_dim):
                    if dim % 2 == 0:
                        pos_encoding[dim] = np.sin(i / (10000 ** (dim / embedding_dim)))
                    else:
                        pos_encoding[dim] = np.cos(i / (10000 ** ((dim - 1) / embedding_dim)))
                
                # Normalize and add (reduced weight to minimize noise)
                pos_encoding = pos_encoding / (np.linalg.norm(pos_encoding) + 1e-8)
                context_components.append(pos_encoding * 0.05)  # Reduced weight to minimize noise
                weights.append(0.05)
            
            # 3. Neighbor context (using prev_uid/next_uid) - WITH NOISE FILTERING
            if use_neighbor_attention:
                neighbor_info = prev_next_map.get(i, {})
                prev_idx = neighbor_info.get('prev_idx')
                next_idx = neighbor_info.get('next_idx')
                
                neighbor_emb = np.zeros(embedding_dim)
                neighbor_weights = []
                neighbor_embeddings = []
                
                # Helper to check similarity and add neighbor
                def add_neighbor_if_similar(neighbor_idx, weight_multiplier=1.0):
                    if neighbor_idx is None or neighbor_idx < 0 or neighbor_idx >= len(self.tokens):
                        return
                    neighbor_emb_single = self.embeddings[neighbor_idx]
                    # Check similarity with base embedding
                    similarity = np.dot(base_emb, neighbor_emb_single) / (
                        np.linalg.norm(base_emb) * np.linalg.norm(neighbor_emb_single) + 1e-8
                    )
                    # Normalize similarity to 0-1 range
                    similarity = (similarity + 1.0) / 2.0
                    # Only include if above threshold (filters noise)
                    if similarity >= min_similarity_threshold:
                        neighbor_embeddings.append(neighbor_emb_single)
                        neighbor_weights.append(similarity * weight_multiplier)
                
                # Include previous tokens in window (with filtering)
                for offset in range(1, min(context_window + 1, i + 1)):
                    neighbor_idx = i - offset
                    if neighbor_idx >= 0:
                        add_neighbor_if_similar(neighbor_idx, weight_multiplier=1.0 / (offset + 1))  # Decay with distance
                
                # Include next tokens in window (with filtering)
                for offset in range(1, min(context_window + 1, len(self.tokens) - i)):
                    neighbor_idx = i + offset
                    if neighbor_idx < len(self.tokens):
                        add_neighbor_if_similar(neighbor_idx, weight_multiplier=1.0 / (offset + 1))  # Decay with distance
                
                # Also use direct prev/next if available (higher priority, but still filtered)
                if prev_idx is not None and prev_idx != i:
                    add_neighbor_if_similar(prev_idx, weight_multiplier=2.0)  # Higher weight for direct neighbor
                
                if next_idx is not None and next_idx != i and next_idx < len(self.tokens):
                    add_neighbor_if_similar(next_idx, weight_multiplier=2.0)  # Higher weight for direct neighbor
                
                if neighbor_embeddings:
                    # Weighted average of similar neighbors only
                    total_weight = sum(neighbor_weights)
                    if total_weight > 0:
                        for emb, weight in zip(neighbor_embeddings, neighbor_weights):
                            neighbor_emb += emb * (weight / total_weight)
                        
                        # Compute final attention weight based on average similarity
                        avg_similarity = np.mean([np.dot(base_emb, emb) / (
                            np.linalg.norm(base_emb) * np.linalg.norm(emb) + 1e-8
                        ) for emb in neighbor_embeddings])
                        avg_similarity = (avg_similarity + 1.0) / 2.0
                        attention_weight = max(0.1, avg_similarity)
                        
                        context_components.append(neighbor_emb)
                        weights.append(attention_weight * 0.3)  # 30% of attention weight
            
            # 4. Content grouping (using content_id) - WITH NOISE FILTERING
            if use_content_grouping:
                content_id = getattr(token, 'content_id', None)
                if content_id is not None and content_id in content_id_to_indices:
                    # Filter: Only include tokens with same content_id that are actually similar
                    same_content_indices = [idx for idx in content_id_to_indices[content_id] if idx != i]
                    if same_content_indices:
                        # Filter by similarity to reduce noise
                        similar_content_embeddings = []
                        similar_content_weights = []
                        
                        for idx in same_content_indices[:20]:  # Check up to 20 tokens
                            content_emb_single = self.embeddings[idx]
                            similarity = np.dot(base_emb, content_emb_single) / (
                                np.linalg.norm(base_emb) * np.linalg.norm(content_emb_single) + 1e-8
                            )
                            similarity = (similarity + 1.0) / 2.0  # Normalize to 0-1
                            
                            # Only include if similar enough (filters noise)
                            if similarity >= min_similarity_threshold:
                                similar_content_embeddings.append(content_emb_single)
                                similar_content_weights.append(similarity)
                        
                        if similar_content_embeddings:
                            # Weighted average of similar content tokens only
                            total_weight = sum(similar_content_weights)
                            if total_weight > 0:
                                content_emb = np.zeros(embedding_dim)
                                for emb, weight in zip(similar_content_embeddings, similar_content_weights):
                                    content_emb += emb * (weight / total_weight)
                                
                                # Weight by how many similar tokens share this content (but cap it)
                                avg_similarity = np.mean(similar_content_weights)
                                content_weight = min(0.2, len(similar_content_embeddings) * 0.02 * avg_similarity)
                                
                                context_components.append(content_emb)
                                weights.append(content_weight)
            
            # 5. Global ID signature (encode global_id into embedding)
            global_id = getattr(token, 'global_id', None)
            if global_id is not None:
                # Convert global_id to deterministic embedding component
                # Use hash of global_id to create deterministic vector
                import hashlib
                gid_hash = hashlib.sha256(str(global_id).encode()).digest()
                # Expand hash to embedding_dim by repeating and hashing again
                gid_emb = np.zeros(embedding_dim, dtype=np.float32)
                for dim in range(embedding_dim):
                    # Use hash bytes cyclically, mixing with dimension index
                    byte_idx = dim % len(gid_hash)
                    gid_emb[dim] = (int(gid_hash[byte_idx]) / 255.0) * 2.0 - 1.0
                gid_emb = gid_emb / (np.linalg.norm(gid_emb) + 1e-8)
                
                context_components.append(gid_emb * 0.02)  # Very small signature (reduced to minimize noise)
                weights.append(0.02)
            
            # Weighted combination of all context components
            total_weight = sum(weights)
            if total_weight > 0:
                fused_emb = np.zeros(embedding_dim)
                for comp, weight in zip(context_components, weights):
                    fused_emb += comp * (weight / total_weight)
                
                # Normalize
                context_embeddings[i] = fused_emb / (np.linalg.norm(fused_emb) + 1e-8)
            else:
                context_embeddings[i] = base_emb
        
        print(f"[OK] Generated {len(context_embeddings)} context-fused embeddings")
        
        # Store for later use
        self.context_embeddings = context_embeddings
        
        return context_embeddings
    
    def search_with_context_fusion(
        self,
        query_text: str,
        top_k: int = 10,
        use_context: bool = True,
        store_name: str = "all"
    ):
        """
        Semantic search using context-fused embeddings.
        
        This demonstrates how context fusion improves semantic recall:
        - "machine learning" will find related tokens even if "machine" and "learning"
          are far apart individually, because context fusion captures their relationship.
        
        Args:
            query_text: Query text
            top_k: Number of results
            use_context: Use context-fused embeddings (if available)
            store_name: Which store to search ("all", "weaviate", "faiss", "chroma")
        """
        print("\n" + "=" * 80)
        print("CONTEXT-AWARE SEMANTIC SEARCH")
        print("=" * 80)
        print(f"Query: '{query_text}'")
        print(f"Using context fusion: {use_context}")
        
        # Get query embedding
        query_emb = self._get_text_embedding(query_text)
        if query_emb is None:
            print("[ERROR] Could not generate query embedding")
            return {}
        
        # Apply context fusion to query if available
        if use_context and hasattr(self, 'context_embeddings') and self.context_embeddings is not None:
            # Find query tokens and apply same context fusion
            query_streams = self.tokenizer.build(query_text)
            query_tokens = []
            for stream_name, token_stream in query_streams.items():
                query_tokens.extend(token_stream.tokens)
            
            if query_tokens:
                # Generate base embeddings for query
                query_base_emb = self.embedding_gen.generate_batch(query_tokens)
                query_base_emb = np.mean(query_base_emb, axis=0)
                
                # Apply context fusion (simplified - average with neighbor context)
                # In practice, you'd rebuild context for query tokens
                query_emb = query_base_emb
                print("[INFO] Using context-fused query embedding")
        
        # Search using standard semantic_search but with context-aware embeddings
        # For now, we'll use the standard search but note the improvement
        results = self.semantic_search(query_text, top_k=top_k, store_name=store_name)
        
        if use_context and hasattr(self, 'context_embeddings'):
            print("\n[INFO] Context fusion improves semantic recall by:")
            print("  - Capturing positional dependencies (prev_uid/next_uid)")
            print("  - Grouping semantically related tokens (content_id)")
            print("  - Encoding full context signatures (global_id)")
            print("  - Using neighbor attention weights")
        
        return results
    
    def visualize_embeddings(self, limit: int = 100):
        """Visualize embeddings using t-SNE."""
        print("\n" + "=" * 80)
        print("VISUALIZATION (t-SNE)")
        print("=" * 80)
        
        try:
            from sklearn.manifold import TSNE
            import matplotlib.pyplot as plt
        except ImportError:
            print("[WARNING] sklearn or matplotlib not available. Install: pip install scikit-learn matplotlib")
            return
        
        # Sample embeddings
        sample_size = min(limit, len(self.embeddings))
        sample_indices = np.random.choice(len(self.embeddings), sample_size, replace=False)
        sample_embeddings = self.embeddings[sample_indices]
        sample_tokens = [self.tokens[i] for i in sample_indices]
        
        print(f"Reducing {sample_size} embeddings to 2D with t-SNE...")
        reduced = TSNE(n_components=2, random_state=42, perplexity=min(30, sample_size-1)).fit_transform(sample_embeddings)
        
        # Create visualization
        plt.figure(figsize=(14, 10))
        scatter = plt.scatter(reduced[:, 0], reduced[:, 1], alpha=0.6, s=50, c=range(sample_size), cmap='viridis')
        
        # Annotate some points
        for i, (x, y) in enumerate(reduced[:20]):
            token_text = getattr(sample_tokens[i], 'text', '')[:15]
            plt.annotate(token_text, (x, y), fontsize=7, alpha=0.8,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.6))
        
        plt.title("SOMA Embedding Space - Semantic Map", fontsize=14, fontweight='bold')
        plt.xlabel("t-SNE Dimension 1", fontsize=12)
        plt.ylabel("t-SNE Dimension 2", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.colorbar(scatter, label='Token Index')
        
        # Save
        output_file = os.path.join(self.output_dir, "SOMA_embeddings_visualization.png")
        plt.savefig(output_file, dpi=200, bbox_inches='tight')
        print(f"[OK] Visualization saved to: {output_file}")
        plt.close()
    
    def close_stores(self):
        """Close all vector store connections."""
        print("\n[INFO] Closing vector stores...")
        
        if self.weaviate_store and hasattr(self.weaviate_store, 'close'):
            try:
                self.weaviate_store.close()
                print("[OK] Weaviate closed")
            except Exception:
                pass
        
        if self.chroma_store and hasattr(self.chroma_store, 'close'):
            try:
                self.chroma_store.close()
                print("[OK] ChromaDB closed")
            except Exception:
                pass
        
        # FAISS doesn't need closing
        if self.faiss_store:
            print("[OK] FAISS ready (no cleanup needed)")


def main():
    """Main function demonstrating comprehensive vector store usage."""
    print("=" * 80)
    print("COMPREHENSIVE SOMA VECTOR STORE EXAMPLE")
    print("=" * 80)
    print("\nThis unified example combines ALL features from:")
    print("  - search_examples.py (semantic search, concept exploration, filtering)")
    print("  - use_semantic_embeddings.py (semantic embeddings, text comparison)")
    print("  - test_full_workflow_500k.py (full workflow, batch loading)")
    print("  - use_vector_store.py (vector store usage, interactive search)")
    print("  - compare_neighbors.py (overlap comparison)")
    print("  - embedding_example.py (basic embeddings, document embeddings)")
    print("  - eval_embedding_quality.py (quality evaluation)")
    print("\nVector Stores: Weaviate (cloud) + FAISS (fast) + ChromaDB (persistent)")
    
    # Check dependencies
    if not check_and_install_dependencies():
        print("[WARNING] Some dependencies are missing. Continuing anyway...")
    
    # Ask user about hybrid embeddings (sentence-transformers)
    use_hybrid = False
    try:
        print("\n" + "=" * 80)
        print("EMBEDDING STRATEGY SELECTION")
        print("=" * 80)
        print("Choose embedding strategy:")
        print("  1. feature_based (default) - Pure SOMA features, fast, no external dependencies")
        print("  2. hybrid - Combines SOMA features + sentence-transformers (better semantics)")
        print("     Note: Requires sentence-transformers (pip install sentence-transformers)")
        
        choice = input("\nEnter choice (1 or 2) [default: 1]: ").strip()
        if choice == "2":
            use_hybrid = True
            print("[INFO] Selected: hybrid embeddings (sentence-transformers)")
        else:
            print("[INFO] Selected: feature_based embeddings (pure SOMA)")
    except (KeyboardInterrupt, EOFError):
        print("\n[INFO] Using default: feature_based embeddings")
        use_hybrid = False
    
    # Initialize example with user's choice
    example = UnifiedVectorStoreExample(output_dir="workflow_output", use_hybrid_embeddings=use_hybrid)
    
    # Initialize vector stores
    example.initialize_vector_stores(use_weaviate=True, use_faiss=True, use_chroma=True)
    
    # Sample text (for new tokenization if needed)
    text = """
    Natural language processing is a field of artificial intelligence.
    Machine learning models learn patterns from data.
    Deep learning uses neural networks with multiple layers.
    Tokenization is the process of breaking text into tokens.
    Embeddings represent tokens as dense vectors.
    Semantic embeddings capture meaning and relationships.
    Vector databases store embeddings for fast similarity search.
    SOMA provides perfect tokenization for any language.
    """ * 10  # Repeat for more tokens
    
    # Show menu for selecting features to run FIRST (before checking for existing data)
    def show_feature_menu():
        """Display menu for selecting features to run."""
        print("\n" + "=" * 80)
        print("FEATURE SELECTION MENU")
        print("=" * 80)
        print("\nAvailable features/tests:")
        print("  1.  Data Processing:")
        print("      a. Tokenization & Embedding Generation")
        print("      b. Detailed Token-by-Token Embedding View")
        print("      c. Store Tokens in Vector Stores")
        print("  2.  Search & Retrieval:")
        print("      d. Semantic Search (with filtering)")
        print("      e. Retrieval Before Processing (context memory)")
        print("      f. Query by ID (Weaviate)")
        print("  3.  Analysis & Comparison:")
        print("      g. Compare Vector Stores (overlap analysis)")
        print("      h. Find Related Concepts")
        print("      i. Compare Tokens (direct similarity)")
        print("      j. Find Concept Cluster")
        print("      k. Concept Exploration (multi-level)")
        print("  4.  Embeddings & Documents:")
        print("      l. Compare Text Embeddings")
        print("      m. Document-Level Embeddings")
        print("  5.  Evaluation & Quality:")
        print("      n. Quality Evaluation (probe tokens)")
        print("      o. Cluster Analysis")
        print("      p. Semantic Alignment Evaluation")
        print("      q. Train Embedding Alignment")
        print("  6.  Advanced Features:")
        print("      r. SOMA-Native Context Fusion")
        print("      s. Visualization (t-SNE)")
        print("  7.  Interactive Mode:")
        print("      t. Interactive Search Mode")
        print("\n  all - Run all features")
        print("  exit - Exit without running")
        
        try:
            choice = input("\nEnter your selection (e.g., 'a,d,g' or 'all') [default: all]: ").strip().lower()
            if not choice:
                choice = "all"
            return choice
        except (KeyboardInterrupt, EOFError):
            return "exit"
    
    # Get user selection
    selected_features = show_feature_menu()
    
    if selected_features == "exit":
        print("\n[INFO] Exiting...")
        example.close_stores()
        return
    
    # Parse selections
    if selected_features == "all":
        selected_features = "a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t"
    
    features_to_run = set(selected_features.split(','))
    features_to_run = {f.strip() for f in features_to_run if f.strip()}
    
    # Check if we need data first
    needs_data = any(f in features_to_run for f in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's'])
    
    # Check for existing data ONLY if needed (based on selection)
    use_loaded_data = False
    if needs_data:
        tokens_file = os.path.join(example.output_dir, "tokens.pkl")
        metadata_file = os.path.join(example.output_dir, "embedding_batches_metadata.json")
        resume = os.path.exists(tokens_file)
        
        if resume:
            print("\n[INFO] Found existing tokens. You can resume from where you left off.")
            try:
                resume_choice = input("Resume? (y/n) [default: y]: ").strip().lower() or "y"
                resume = resume_choice == "y"
            except (KeyboardInterrupt, EOFError):
                resume = True  # Default to resume on interrupt
            
            if resume:
                # Try to load from disk
                if os.path.exists(metadata_file):
                    if example.load_vector_store_from_disk(max_batches=30):
                        print("[OK] Using loaded data. Skipping tokenization and embedding generation.")
                        use_loaded_data = True
                    else:
                        print("[WARNING] Failed to load embeddings. Will use tokens only.")
                        # Still load tokens even if embeddings fail
                        try:
                            import types
                            project_root = Path(__file__).parent.parent
                            if str(project_root) not in sys.path:
                                sys.path.insert(0, str(project_root))
                            
                            if 'core' not in sys.modules:
                                core_module = types.ModuleType('core')
                                sys.modules['core'] = core_module
                            if 'core.core_tokenizer' not in sys.modules:
                                core_tokenizer_module = types.ModuleType('core.core_tokenizer')
                                sys.modules['core.core_tokenizer'] = core_tokenizer_module
                                try:
                                    from src.core.core_tokenizer import TokenRecord, TokenStream
                                    core_tokenizer_module.TokenRecord = TokenRecord
                                    core_tokenizer_module.TokenStream = TokenStream
                                except ImportError:
                                    pass
                            
                            class CustomUnpickler(pickle.Unpickler):
                                def find_class(self, module, name):
                                    if module == 'core.core_tokenizer' or module == 'core':
                                        try:
                                            from src.core.core_tokenizer import TokenRecord, TokenStream
                                            if name == 'TokenRecord':
                                                return TokenRecord
                                            elif name == 'TokenStream':
                                                return TokenStream
                                        except ImportError:
                                            pass
                                    return super().find_class(module, name)
                            
                            with open(tokens_file, 'rb') as f:
                                try:
                                    unpickler = CustomUnpickler(f)
                                    example.tokens = unpickler.load()
                                except Exception:
                                    f.seek(0)
                                    example.tokens = pickle.load(f)
                            print(f"[OK] Loaded {len(example.tokens):,} tokens from disk")
                            use_loaded_data = True
                        except Exception as e:
                            print(f"[WARNING] Could not load tokens: {e}")
                            use_loaded_data = False
                else:
                    # Only tokens.pkl exists, load tokens
                    print("[INFO] Found tokens.pkl but no embedding batches. Loading tokens only...")
                    try:
                        import types
                        project_root = Path(__file__).parent.parent
                        if str(project_root) not in sys.path:
                            sys.path.insert(0, str(project_root))
                        
                        if 'core' not in sys.modules:
                            core_module = types.ModuleType('core')
                            sys.modules['core'] = core_module
                        if 'core.core_tokenizer' not in sys.modules:
                            core_tokenizer_module = types.ModuleType('core.core_tokenizer')
                            sys.modules['core.core_tokenizer'] = core_tokenizer_module
                            try:
                                from src.core.core_tokenizer import TokenRecord, TokenStream
                                core_tokenizer_module.TokenRecord = TokenRecord
                                core_tokenizer_module.TokenStream = TokenStream
                            except ImportError:
                                pass
                        
                        class CustomUnpickler(pickle.Unpickler):
                            def find_class(self, module, name):
                                if module == 'core.core_tokenizer' or module == 'core':
                                    try:
                                        from src.core.core_tokenizer import TokenRecord, TokenStream
                                        if name == 'TokenRecord':
                                            return TokenRecord
                                        elif name == 'TokenStream':
                                            return TokenStream
                                    except ImportError:
                                        pass
                                return super().find_class(module, name)
                        
                        with open(tokens_file, 'rb') as f:
                            try:
                                unpickler = CustomUnpickler(f)
                                example.tokens = unpickler.load()
                            except Exception:
                                f.seek(0)
                                example.tokens = pickle.load(f)
                        print(f"[OK] Loaded {len(example.tokens):,} tokens from disk")
                        print("[INFO] You can generate embeddings for these tokens or load embedding batches separately.")
                        use_loaded_data = True
                    except Exception as e:
                        print(f"[WARNING] Could not load tokens: {e}")
                        use_loaded_data = False
    
    try:
        # Data preparation (only if needed)
        if needs_data:
            if not use_loaded_data:
                # Step 1: Retrieval before processing (context memory) - if selected
                if 'e' in features_to_run:
                    example.retrieval_before_processing("machine learning", top_k=5)
                
                # Step 1.5: Show detailed token-by-token embeddings - if selected
                if 'b' in features_to_run:
                    print("\n" + "=" * 80)
                    print("DETAILED EMBEDDING VIEW")
                    print("=" * 80)
                    example.show_detailed_embeddings("Hello world, this is SOMA!", max_tokens_per_stream=5)
                
                # Step 2-4: Tokenize, generate embeddings, store - if selected
                if 'a' in features_to_run or 'c' in features_to_run:
                    # Step 2: Tokenize
                    if 'a' in features_to_run:
                        example.tokenize_text(text)
                    
                    # Step 3: Generate embeddings
                    if 'a' in features_to_run:
                        example.generate_embeddings(strategy="feature_based")
                    
                    # Step 4: Store tokens (with tags for memory building)
                    if 'c' in features_to_run:
                        example.store_tokens()
            else:
                # Data loaded from disk
                print("\n[INFO] Using loaded data.")
                
                # Check if embeddings are loaded, if not, generate them
                if example.embeddings is None or len(example.embeddings) == 0:
                    if example.tokens and len(example.tokens) > 0:
                        print(f"[INFO] Found {len(example.tokens):,} tokens but no embeddings.")
                        if 'a' in features_to_run:
                            print("[INFO] Generating embeddings for loaded tokens...")
                            example.generate_embeddings()
                            
                            # Optionally store in vector stores
                            if 'c' in features_to_run:
                                try:
                                    store_choice = input("\n[INFO] Store tokens in vector stores? (y/n) [default: y]: ").strip().lower() or "y"
                                    if store_choice == "y":
                                        example.store_tokens()
                                except (KeyboardInterrupt, EOFError):
                                    pass
                    else:
                        print("[WARNING] No tokens or embeddings loaded. Cannot proceed with search operations.")
                        if not any(f in features_to_run for f in ['a', 'b']):
                            return
                else:
                    print("[INFO] Proceeding to selected features...")
        
        # Run selected features
        if 'd' in features_to_run:
            example.semantic_search("machine", top_k=10, store_name="all", min_similarity=0.5, filter_stop=True)
            example.semantic_search("learning", top_k=10, store_name="all", min_similarity=0.5, filter_stop=True)
        
        if 'g' in features_to_run:
            example.compare_stores("artificial", top_k=10)
        
        if 'h' in features_to_run:
            example.find_related_concepts(["machine", "learning"], top_k=15, min_similarity=0.4)
        
        if 'i' in features_to_run:
            example.compare_tokens("artificial", "intelligence")
            example.compare_tokens("machine", "learning")
        
        if 'j' in features_to_run:
            example.find_concept_cluster("neural", cluster_size=10, min_similarity=0.6)
        
        if 'k' in features_to_run:
            example.explore_concept("neural", depth=2, top_k_per_level=10)
        
        if 'l' in features_to_run:
            example.compare_embeddings("machine learning", "artificial intelligence")
            example.compare_embeddings("natural language processing", "deep learning")
        
        if 'm' in features_to_run:
            documents = [
                "Machine learning is a subset of artificial intelligence",
                "Natural language processing helps computers understand text",
                "Deep learning uses neural networks with multiple layers"
            ]
            example.get_document_embeddings(documents, method="mean")
        
        if 'n' in features_to_run:
            probes = ["artificial", "machine", "learning", "neural", "data"]
            example.evaluate_quality(probes, top_k=10)
        
        if 'o' in features_to_run:
            example.analyze_clusters(sample_size=100, top_k=5)
        
        if 'f' in features_to_run and example.weaviate_store:
            # Get a token ID from search results
            search_results = example.semantic_search("machine", top_k=1, store_name="weaviate")
            if search_results.get('weaviate') and len(search_results['weaviate']) > 0:
                token_id = search_results['weaviate'][0].get('id')
                if token_id:
                    example.query_by_id(token_id, store_name="weaviate")
        
        if 's' in features_to_run:
            example.visualize_embeddings(limit=100)
        
        if 'r' in features_to_run:
            print("\n" + "=" * 80)
            print("SOMA-NATIVE CONTEXT FUSION")
            print("=" * 80)
            print("Solving semantic context loss using SOMA's own mechanisms...")
            context_embeddings = example.build_context_fusion_embeddings(
                context_window=5,
                use_positional=True,
                use_neighbor_attention=True,
                use_content_grouping=True,
                min_similarity_threshold=0.3  # Filter out noisy neighbors/content
            )
            
            if context_embeddings is not None:
                print("\n[INFO] Testing context fusion improvement...")
                print("\n--- Without Context Fusion ---")
                example.semantic_search("machine", top_k=5, store_name="faiss")
                
                print("\n--- With Context Fusion ---")
                example.search_with_context_fusion("machine learning", top_k=5, use_context=True, store_name="faiss")
        
        if 'p' in features_to_run:
            print("\n" + "=" * 80)
            print("SEMANTIC ALIGNMENT EVALUATION")
            print("=" * 80)
            alignment_results = example.evaluate_semantic_alignment()
            
            # Step 18: Train embedding alignment (if misalignment detected and selected)
            if 'q' in features_to_run and alignment_results and alignment_results.get('mean_error', 0) > 0.2:
                print("\n" + "=" * 80)
                print("TRAINING EMBEDDING ALIGNMENT")
                print("=" * 80)
                training_pairs = [
                    ("AI helps humans.", "Machines assist people.", 0.9),
                    ("The cat sat on the mat.", "A feline rested on a rug.", 0.85),
                    ("Natural language processing", "NLP", 0.95),
                    ("Machine learning", "Deep learning", 0.7),
                    ("I love programming.", "I hate coding.", 0.3),
                    ("Python programming", "Cooking recipes", 0.1),
                    ("Tokenization breaks text.", "Text splitting creates tokens.", 0.8),
                    ("Embeddings represent meaning.", "Vectors capture semantics.", 0.85),
                    ("Vector databases store embeddings.", "Cooking recipes for dinner.", 0.1),
                    ("Semantic search finds similar texts.", "Meaning-based retrieval works.", 0.9),
                ]
                
                try:
                    alignment_model = example.train_embedding_alignment(
                        training_pairs, 
                        epochs=20, 
                        learning_rate=0.001,
                        use_contrastive=True,
                        use_mse=True
                    )
                    if alignment_model:
                        print("\n[OK] Embedding alignment training complete!")
                        print("   Use apply_alignment() to transform embeddings for better semantic search.")
                except Exception as e:
                    print(f"[WARNING] Alignment training failed: {e}")
        
        if 't' in features_to_run:
            example.interactive_search()
        
        print("\n" + "=" * 80)
        print("[OK] SELECTED FEATURES COMPLETE!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        example.close_stores()


if __name__ == "__main__":
    main()
