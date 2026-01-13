# examples/eval_embedding_quality.py
import sys
import os
import json
import numpy as np
import pickle
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings.embedding_generator import somaEmbeddingGenerator
from src.embeddings.semantic_trainer import somaSemanticTrainer
from src.embeddings.vector_store import ChromaVectorStore, FAISSVectorStore
from src.core.core_tokenizer import TextTokenizer, all_tokenizations

# Import the quick_load_vector_store function from search_examples
# Add examples directory to path for importing
examples_dir = Path(__file__).parent
if str(examples_dir) not in sys.path:
    sys.path.insert(0, str(examples_dir))

try:
    # Try to import from search_examples
    import importlib.util
    spec = importlib.util.spec_from_file_location("search_examples", examples_dir / "search_examples.py")
    search_examples = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(search_examples)
    quick_load_vector_store = search_examples.quick_load_vector_store
    find_token_embedding = search_examples.find_token_embedding
except (ImportError, AttributeError, Exception) as e:
    # Define it here if import fails
    print(f"[WARNING] Could not import from search_examples: {e}")
    print("[INFO] Using local implementation...")
    def quick_load_vector_store(output_dir="workflow_output", max_batches=30):
        """Quickly load vector store (optimized version)."""
        print("[INFO] Loading vector store...")
        
        # Load tokens with proper import handling
        tokens_file = os.path.join(output_dir, "tokens.pkl")
        try:
            # Use the load_tokens function from test_full_workflow_500k if available
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent.parent
            src_path = project_root / 'src'
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))
            
            # Create mock modules for pickle compatibility
            import types
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
            
            # Create custom unpickler
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
                    all_tokens = unpickler.load()
                except Exception:
                    f.seek(0)
                    all_tokens = pickle.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load tokens: {e}")
            return None, None, None, None
        
        # Load metadata
        metadata_file = os.path.join(output_dir, "embedding_batches_metadata.json")
        if not os.path.exists(metadata_file):
            print(f"[ERROR] Metadata file not found: {metadata_file}")
            return None, None, None, None
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        batch_files = metadata.get("batch_files", [])[:max_batches]
        embedding_dim = metadata.get("embedding_dim", 768)
        batch_size = metadata.get("batch_size", 50000)
        
        # Create vector store
        vector_store = FAISSVectorStore(embedding_dim=embedding_dim)
        
        # Load batches
        max_tokens = max_batches * batch_size
        sample_tokens = all_tokens[:min(max_tokens, len(all_tokens))]
        
        total_added = 0
        for batch_idx, batch_file in enumerate(batch_files):
            if not os.path.exists(batch_file):
                continue
            
            batch_emb = np.load(batch_file)
            batch_start = batch_idx * batch_size
            batch_end = min(batch_start + len(batch_emb), len(sample_tokens))
            batch_tokens = sample_tokens[batch_start:batch_end]
            
            # Add in chunks
            for chunk_start in range(0, len(batch_tokens), 10000):
                chunk_end = min(chunk_start + 10000, len(batch_tokens))
                vector_store.add_tokens(
                    batch_tokens[chunk_start:chunk_end],
                    batch_emb[chunk_start:chunk_end]
                )
            
            total_added += len(batch_tokens)
            if (batch_idx + 1) % 10 == 0:
                print(f"  Loaded {batch_idx + 1}/{len(batch_files)} batches ({total_added:,} tokens)")
        
        print(f"[OK] Loaded {total_added:,} tokens into vector store\n")
        return vector_store, sample_tokens, batch_size, batch_files
    
    def find_token_embedding(token_text, sample_tokens, batch_files, batch_size):
        """Find embedding for a token."""
        for idx, token in enumerate(sample_tokens):
            if getattr(token, 'text', '').lower() == token_text.lower():
                batch_idx = idx // batch_size
                if batch_idx < len(batch_files) and os.path.exists(batch_files[batch_idx]):
                    be = np.load(batch_files[batch_idx])
                    local_idx = idx % batch_size
                    if local_idx < len(be):
                        return be[local_idx]
        return None

# PROBES
probes = ["artificial", "machine", "learning", "neural", "data", "india", "sport", "cat", "dog"]

# Load vector store
print("[INFO] Loading vector store...")
vector_store, sample_tokens, batch_size, batch_files = quick_load_vector_store("workflow_output", max_batches=30)

if vector_store is None:
    print("[ERROR] Failed to load vector store. Make sure you have run test_full_workflow_500k.py first.")
    sys.exit(1)

# Helper to get neighbors
def top_k_neighbors(vstore, token_text, k=10):
    """Get top k neighbors for a token."""
    emb = find_token_embedding(token_text, sample_tokens, batch_files, batch_size)
    if emb is None:
        return []
    return vstore.search(emb, top_k=k)

# Run probes and print
print("\n[INFO] Running probes...")
for p in probes:
    results = top_k_neighbors(vector_store, p, k=10)
    print(f"--- {p} ---")
    if results:
        for r in results:
            print(f"  {r.get('text', 'N/A')}: {r.get('distance', None):.4f}")
    else:
        print("  No results found")
    print()
