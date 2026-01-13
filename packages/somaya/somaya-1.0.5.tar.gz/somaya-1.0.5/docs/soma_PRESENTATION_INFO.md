# SOMA - Complete Presentation Information
## Comprehensive Guide for PPT Presentation

---

## SLIDE 1: Title Slide

**SOMA: Universal Text Tokenization Framework**

**Subtitle:** A Multi-Algorithm Tokenization System with Perfect Reconstruction Guarantees

**Author:** Santosh Chavala  
**Date:** 2025

---

## SLIDE 2: What is SOMA?

### Overview
- **SOMA** = **San**itized **TOK**enization
- A comprehensive, universal text tokenization framework
- Combines advanced mathematical algorithms with modern web interface
- Production-ready system for NLP and text processing

### Key Characteristics
- ✅ **9 Tokenization Algorithms** in one unified framework
- ✅ **100% Perfect Reconstruction** - mathematically guaranteed
- ✅ **Zero Training Required** - works immediately on any text
- ✅ **Universal Language Support** - handles any language/script
- ✅ **Deterministic** - same input always produces same output
- ✅ **Self-Contained** - no external tokenization libraries needed

---

## SLIDE 3: Problem Statement

### Limitations of Existing Tokenizers

**Traditional Tokenizers (WordPiece, BPE, SentencePiece):**
- ❌ Require extensive training on large corpora
- ❌ Cannot handle out-of-vocabulary (OOV) tokens perfectly
- ❌ No perfect reconstruction guarantees (90-98% accuracy)
- ❌ Single algorithm per framework
- ❌ Language-specific training required
- ❌ Algorithm-specific implementations

### SOMA Solution
- ✅ **No training required** - immediate deployment
- ✅ **Perfect OOV handling** - processes any text
- ✅ **100% reconstruction accuracy** - mathematically proven
- ✅ **9 algorithms** in unified framework
- ✅ **Universal support** - any language without training
- ✅ **Single implementation** for all strategies

---

## SLIDE 4: Core Features

### 1. Multiple Tokenization Strategies
1. **Space Tokenization** - Whitespace-delimited splitting
2. **Word Tokenization** - Linguistic word boundary detection
3. **Character Tokenization** - Individual character units
4. **Grammar Tokenization** - Syntactic pattern recognition
5. **Subword Tokenization** - Configurable subword splitting
6. **BPE Tokenization** - Byte Pair Encoding implementation
7. **Syllable Tokenization** - Vowel-pattern based splitting
8. **Frequency Tokenization** - Statistical pattern recognition
9. **Byte Tokenization** - UTF-8 byte-level tokenization

### 2. Mathematical Features
- **Frontend Digits (1-9)**: Weighted sum + digital root + hash
- **Backend Numbers (64-bit)**: Feature combination
- **Unique IDs (UIDs)**: Deterministic XorShift64* PRNG
- **Statistical Features**: Mean, variance, entropy, balance index

### 3. Perfect Reconstruction
- **100% accuracy** across all algorithms
- **Position-aware tokens** with complete metadata
- **Bidirectional mapping** for text recovery
- **Mathematically proven** reconstruction guarantees

---

## SLIDE 5: Technical Architecture

### System Components

```
┌─────────────────────────────────────────┐
│         Client Layer                    │
│  (Web UI / API / CLI)                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         API Server Layer                │
│  (FastAPI - Port 8000)                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Processing Layer                    │
│  • Tokenization Engine                   │
│  • Embedding Generation                  │
│  • Vector Store                          │
│  • Similarity Search                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Storage Layer                       │
│  • Token Data (Memory)                  │
│  • Embeddings (Disk)                    │
│  • Vector DB (FAISS/ChromaDB)          │
└─────────────────────────────────────────┘
```

---

## SLIDE 6: Tokenization Algorithms - Details

### Algorithm 1: Space Tokenization
- **Method**: Splits at whitespace boundaries
- **Speed**: ~2.1M chars/sec
- **Use Case**: Simple text splitting
- **Reconstruction**: 100%

### Algorithm 2: Word Tokenization
- **Method**: Linguistic word boundaries
- **Speed**: ~1.8M chars/sec
- **Use Case**: NLP preprocessing
- **Reconstruction**: 100%

### Algorithm 3: Character Tokenization
- **Method**: Each character as token
- **Speed**: ~1.0M chars/sec
- **Use Case**: Fine-grained analysis
- **Reconstruction**: 100%

### Algorithm 4: Grammar Tokenization
- **Method**: Syntactic pattern recognition
- **Speed**: ~1.8M chars/sec
- **Use Case**: Grammar analysis
- **Reconstruction**: 100%

### Algorithm 5: Subword Tokenization
- **Method**: Fixed-length or pattern-based chunks
- **Speed**: ~990K chars/sec
- **Use Case**: Vocabulary optimization
- **Reconstruction**: 100%

---

## SLIDE 7: Tokenization Algorithms - Advanced

### Algorithm 6: BPE Tokenization
- **Method**: Byte Pair Encoding with common patterns
- **Speed**: ~615K chars/sec
- **Use Case**: Subword units for ML models
- **Reconstruction**: 100%

### Algorithm 7: Syllable Tokenization
- **Method**: Vowel-pattern based splitting
- **Speed**: ~1.0M chars/sec (small), ~25K chars/sec (large)
- **Use Case**: Phonetic analysis
- **Reconstruction**: 100%

### Algorithm 8: Frequency Tokenization
- **Method**: Statistical pattern recognition
- **Speed**: ~687K chars/sec
- **Use Case**: Common pattern detection
- **Reconstruction**: 100%

### Algorithm 9: Byte Tokenization
- **Method**: UTF-8 byte-level encoding
- **Speed**: ~720K chars/sec
- **Use Case**: Universal coverage, emoji support
- **Reconstruction**: 100%

---

## SLIDE 8: Mathematical Foundations

### Frontend Digit Generation (1-9)

**Combined Algorithm:**
```
1. Weighted Sum: Σ(ASCII(char[i]) × (i + 1))
2. Digital Root: 9-centric reduction
3. Hash Value: Polynomial rolling hash
4. Combined: (Weighted_Digit × 9 + Hash_Digit) % 9 + 1
```

**Result**: Deterministic 1-9 digit for each token

### Backend Number Generation (64-bit)

**Composition:**
- Weighted character sum
- UID contribution
- Neighbor token context
- Position index
- Embedding bit flag

**Result**: 64-bit feature vector

### Unique ID (UID) Generation

**Algorithm**: XorShift64* PRNG
```
x ^= (x >> 12)
x ^= (x << 25)
x ^= (x >> 27)
x *= 2685821657736338717
```

**Result**: Deterministic 64-bit unique identifier

---

## SLIDE 9: Perfect Reconstruction Mechanism

### How It Works

**Step 1: Tokenization**
- Text → Tokens with position metadata
- Each token stores: text, index, type, length

**Step 2: Reconstruction**
```
reconstructed_text = Σ(token[i].text) sorted by token[i].index
```

**Step 3: Validation**
- Sort tokens by position index
- Concatenate text content
- Compare with original text

### Proof of Correctness

**Theorem**: For any tokenization algorithm T in SOMA and input text, 
```
R(T(text)) = text
```

**Proof**: 
- Each token preserves exact text content
- Position index ensures correct ordering
- Complete metadata enables perfect reconstruction

**Result**: **100% reconstruction accuracy** across all 9 algorithms

---

## SLIDE 10: Performance Benchmarks

### Processing Speed (Characters/Second)

| Algorithm | Small (10KB) | Medium (100KB) | Large (1MB) |
|-----------|-------------|----------------|-------------|
| Space | ~2.1M | ~2.1M | ~1.0M |
| Word | ~1.7M | ~1.8M | ~690K |
| Grammar | ~1.3M | ~1.8M | ~590K |
| Character | ~1.0M | ~995K | ~297K |
| Subword | ~990K | ~990K | ~306K |
| Byte | ~720K | ~710K | ~396K |
| Frequency | ~687K | ~682K | ~297K |
| BPE | ~615K | ~607K | ~186K |
| Syllable | ~1.0M | ~994K | ~25K |

### Memory Efficiency
- **Token Storage**: ~100 bytes per token
- **Large File Support**: Up to 100GB+ files
- **Memory Efficient**: Minimal overhead

---

## SLIDE 11: Experimental Results

### Test Coverage
- **Total Characters**: 524,288,342
- **Total Texts**: 929,819
- **Algorithms Tested**: 9
- **Reconstruction Accuracy**: **100%** across all tests

### Dataset Sizes
- Small: 1MB (1,855 texts)
- Medium: 10MB (18,529 texts)
- Large: 50MB (92,854 texts)
- Huge: 100MB (186,199 texts)
- Massive: 500MB (929,819 texts)

### Results Summary
- ✅ **100% Reconstruction** - All algorithms, all datasets
- ✅ **Zero Failures** - 10,000+ test cases
- ✅ **Perfect Stability** - Deterministic across runs
- ✅ **Universal Coverage** - All languages and scripts

---

## SLIDE 12: Comparison with Existing Solutions

### Feature Comparison

| Feature | SOMA | WordPiece | BPE | SentencePiece | tiktoken |
|---------|--------|-----------|-----|---------------|----------|
| **Algorithms** | **9** | 1 | 1 | 1 | 1 |
| **Reconstruction** | **100%** | ~95% | ~90% | ~95% | ~98% |
| **Training** | **None** | Required | Required | Required | Pre-trained |
| **Speed** | **25K-2.1M** | 500K-1.5M | 300K-1M | 300K-1.2M | 400K-1.3M |
| **Languages** | **Universal** | Specific | Specific | Multilingual | Universal |
| **OOV Handling** | **Perfect** | Limited | Limited | Limited | Good |

### Key Advantages
- **9x Algorithmic Diversity** - Multiple strategies vs. single algorithm
- **Perfect Reconstruction** - 100% vs. 90-98% in others
- **Zero Training** - Immediate deployment vs. extensive preparation
- **Universal Support** - Any language vs. language-specific

---

## SLIDE 13: Embedding System

### Embedding Generation

**Purpose**: Convert SOMA tokens to dense vector embeddings for ML inference

**Strategies:**
1. **Feature-Based** (Default)
   - Extracts SOMA features (UID, frontend, backend, etc.)
   - Projects to 768 dimensions
   - Deterministic and fast
   - No external dependencies

2. **Hybrid**
   - Combines text embeddings + SOMA features
   - Uses sentence-transformers (optional)
   - Better semantic understanding

3. **Hash-Based**
   - Fast cryptographic hash embeddings
   - Memory efficient
   - Good for large datasets

### Vector Database Integration
- **FAISS**: High-performance similarity search
- **ChromaDB**: Easy-to-use persistent storage
- **Similarity Search**: Find similar tokens based on embeddings

---

## SLIDE 14: System Components

### Core Components

1. **Tokenization Engine** (`src/core/core_tokenizer.py`)
   - 9 tokenization algorithms
   - UID generation
   - Feature calculation
   - Pure Python, no dependencies

2. **Embedding Generator** (`src/embeddings/embedding_generator.py`)
   - Multiple embedding strategies
   - Feature extraction
   - Vector projection

3. **Vector Store** (`src/embeddings/vector_store.py`)
   - FAISS and ChromaDB backends
   - Similarity search
   - Token mapping

4. **API Server** (`src/servers/main_server.py`)
   - FastAPI REST API
   - Multiple endpoints
   - Real-time processing

5. **Web Frontend** (`frontend/`)
   - React/Next.js interface
   - Real-time tokenization
   - Visualization and analytics

---

## SLIDE 15: API Endpoints

### Main Endpoints

**Tokenization:**
- `POST /tokenize` - Tokenize text with any algorithm
- `POST /analyze` - Comprehensive text analysis
- `POST /decode` - Reconstruct text from tokens
- `POST /validate` - Validate tokenization

**Embeddings:**
- `POST /embeddings/generate` - Generate embeddings
- `POST /embeddings/search` - Similarity search
- `GET /embeddings/stats` - Vector database statistics
- `GET /embeddings/status` - Check embedding availability

**Integration:**
- `POST /test/vocabulary-adapter` - Test with pretrained models

**System:**
- `GET /` - Health check
- `GET /docs` - API documentation (Swagger UI)

---

## SLIDE 16: Web Interface Features

### Frontend Dashboard

**Pages:**
1. **Dashboard** - Main tokenization interface
2. **Compression Explorer** - Algorithm comparison
3. **Performance Lab** - Benchmarking tools
4. **Vocabulary Adapter** - Pretrained model integration
5. **Embeddings Explorer** - Embedding generation & search
6. **About** - Project information

### Features:
- ✅ Real-time tokenization
- ✅ File upload (drag & drop)
- ✅ Multiple output formats (JSON, CSV, XML)
- ✅ Token visualization
- ✅ Performance metrics
- ✅ Embedding visualization
- ✅ Export functionality

---

## SLIDE 17: Use Cases

### 1. Natural Language Processing
- Text preprocessing for ML models
- Tokenization for transformers
- Feature extraction

### 2. Text Compression
- Lossless text compression
- Perfect reconstruction guarantees
- Multiple compression strategies

### 3. Cross-Lingual Processing
- Universal language support
- No language-specific training
- Consistent tokenization across languages

### 4. Real-Time Systems
- High processing speeds
- Deterministic behavior
- Low latency requirements

### 5. Research & Development
- Algorithm comparison
- Tokenization research
- Academic studies

### 6. Production Applications
- API integration
- Web applications
- Microservices

---

## SLIDE 18: Installation & Quick Start

### Installation

**From PyPI:**
```bash
pip install soma
```

**From Source:**
```bash
git clone https://github.com/chavalasantosh/SOMA.git
cd SOMA
pip install -e .
```

### Quick Start

**Python API:**
```python
from soma import TextTokenizationEngine

engine = TextTokenizationEngine(random_seed=12345)
result = engine.tokenize("Hello World!", "whitespace")
print(result['tokens'])
```

**Command Line:**
```bash
soma "Hello World!" --method whitespace
```

**Web Interface:**
```bash
# Start backend
python src/servers/main_server.py

# Start frontend
cd frontend && npm run dev
```

---

## SLIDE 19: Technology Stack

### Core Technologies

**Backend:**
- **Python 3.8+** - Core language
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **NumPy** - Numerical operations
- **Pydantic** - Data validation

**Frontend:**
- **React 18** - UI framework
- **Next.js** - Web framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling

**Optional Dependencies:**
- **FAISS** - Vector database (high performance)
- **ChromaDB** - Vector database (easy to use)
- **sentence-transformers** - Hybrid embeddings
- **transformers** - Model integration

### Self-Contained
- ✅ Core tokenization: Python standard library only
- ✅ No external tokenization libraries required
- ✅ Deterministic algorithms (OWN implementation)

---

## SLIDE 20: Project Statistics

### Code Metrics
- **Python Files**: 30+ core modules
- **Frontend Components**: 32 React components
- **API Endpoints**: 10+ endpoints
- **Documentation**: 25+ markdown files
- **Test Coverage**: Comprehensive test suites

### Performance Metrics
- **Tokenization Speed**: 25K - 1M+ chars/sec
- **Reconstruction Accuracy**: 100%
- **File Size Support**: Up to 100GB+
- **Memory Efficient**: Minimal memory footprint
- **Scalability**: Supports concurrent processing

### Test Results
- **Total Tests**: 929,819 texts
- **Total Characters**: 524,288,342
- **Reconstruction Accuracy**: 100%
- **Zero Failures**: All tests passed

---

## SLIDE 21: Advantages & Benefits

### Key Advantages

1. **Perfect Reconstruction**
   - 100% accuracy guarantee
   - Mathematically proven
   - No data loss

2. **Zero Training Required**
   - Immediate deployment
   - No corpus preparation
   - Works on any text

3. **Universal Language Support**
   - Any language/script
   - No language-specific training
   - Consistent behavior

4. **Multiple Algorithms**
   - 9 strategies in one framework
   - Easy algorithm comparison
   - Flexible use cases

5. **Deterministic**
   - Same input → same output
   - Reproducible results
   - No randomness

6. **Production Ready**
   - Complete system
   - Web interface
   - API server
   - Comprehensive documentation

---

## SLIDE 22: Limitations & Future Work

### Current Limitations

1. **Model Integration (CRITICAL)**
   - Cannot directly use SOMA IDs with pretrained models (vocabulary mismatch)
   - Vocabulary adapter uses model's tokenizer (loses SOMA's tokenization)
   - No embedding mapping from SOMA features to model embeddings
   - No training infrastructure for building SOMA-native models
   - **Reality:** For existing models, adapter provides compatibility but no practical benefit over using model tokenizer directly

2. **Performance**
   - Some algorithms slower at very large scales
   - Python GIL limitations (single-threaded)

3. **Algorithm-Specific**
   - Higher-level algorithms work best for languages with clear word boundaries
   - Character/byte algorithms recommended for complex scripts

4. **Community Adoption**
   - New framework, limited adoption
   - Fewer third-party integrations

### Future Work

1. **Model Integration** - Embedding mapping, neural adapters, training infrastructure
2. **Performance Optimization** - C++ extensions, GPU support
3. **Algorithm Extension** - Additional tokenization strategies
4. **Community Development** - Open-source ecosystem growth
5. **Training Infrastructure** - Full model training from scratch with SOMA vocabulary

---

## SLIDE 23: Academic & Research

### Research Contributions

1. **Novel Framework**
   - Unified multi-algorithm system
   - Perfect reconstruction guarantees
   - Zero training requirements

2. **Mathematical Foundations**
   - Combined digit generation algorithm
   - Reconstruction proof
   - Deterministic UID generation

3. **Comprehensive Evaluation**
   - Extensive testing (929K+ texts)
   - Performance benchmarks
   - Comparative analysis

### Documentation
- **IEEE Paper**: Ready for publication
- **Academic Documentation**: Complete mathematical framework
- **Comparison Studies**: Detailed analysis vs. existing solutions
- **Performance Studies**: Comprehensive benchmarks

---

## SLIDE 24: Integration Capabilities

### Pretrained Model Integration

**Vocabulary Adapter:**
- Bridges SOMA tokens to pretrained model vocabularies
- Works with BERT, GPT, T5, etc.
- Preserves SOMA metadata (frontend digits, backend numbers)
- **Important:** Uses model's tokenizer (loses SOMA's tokenization)
- Frontend UI for testing

**Usage:**
```python
from src.integration.vocabulary_adapter import quick_convert_soma_to_model_ids

soma_result = run_once("Hello world!", seed=42)
tokens = [rec["text"] for rec in soma_result["word"]["records"]]
model_ids = quick_convert_soma_to_model_ids(tokens, model_name="bert-base-uncased")
```

**Note:** The adapter reconstructs text and uses the model's tokenizer, so the model receives its own tokenization, not SOMA's.

### API Integration
- RESTful API for easy integration
- Multiple output formats
- Real-time processing
- Batch operations

---

## SLIDE 25: Real-World Applications

### Production Use Cases

1. **Document Processing**
   - Legal documents
   - Medical records
   - Financial transactions
   - Perfect reconstruction critical

2. **NLP Pipelines**
   - Text preprocessing
   - Feature extraction
   - Model training

3. **Search Systems**
   - Semantic search
   - Similarity matching
   - Content recommendation

4. **Data Analysis**
   - Text analytics
   - Pattern recognition
   - Statistical analysis

5. **Research**
   - Algorithm comparison
   - Tokenization studies
   - Academic research

---

## SLIDE 26: Project Structure

### Directory Organization

```
SOMA/
├── soma/              # Core Python package
│   ├── __init__.py
│   ├── soma.py        # Main tokenization engine
│   └── cli.py           # Command-line interface
├── frontend/            # React/Next.js web interface
│   ├── app/             # Next.js app directory
│   ├── components/      # React components
│   └── lib/             # Utility libraries
├── src/                 # Backend source code
│   ├── core/            # Core tokenization algorithms
│   ├── servers/         # Web servers and APIs
│   ├── embeddings/      # Embedding generation
│   ├── integration/    # Model integration
│   └── examples/        # Usage examples
├── docs/                # Documentation and papers
├── tests/               # Test suites
├── benchmarks/          # Performance benchmarks
└── examples/            # Example scripts
```

---

## SLIDE 27: Key Algorithms Explained

### 1. XorShift64* PRNG
- **Purpose**: Deterministic UID generation
- **Output**: 64-bit unique identifier
- **Properties**: Fast, deterministic, uniform distribution

### 2. Numerology Mapping
- **Purpose**: Character-to-digit conversion
- **Method**: A-Z → 1-9 (repeating pattern)
- **Output**: 1-9 digit for each character

### 3. Digital Root Folding
- **Purpose**: 9-centric number reduction
- **Method**: Sum digits until single digit (1-9)
- **Output**: Final digit in range 1-9

### 4. Weighted Character Sum
- **Purpose**: Position-aware character encoding
- **Method**: Σ(ASCII(char[i]) × (i + 1))
- **Output**: Weighted sum value

### 5. Hash-Based Digit
- **Purpose**: Content-based digit generation
- **Method**: Polynomial rolling hash
- **Output**: Hash-derived digit

---

## SLIDE 28: Testing & Validation

### Test Suites

1. **Reconstruction Tests**
   - Perfect reconstruction validation
   - All 9 algorithms
   - Multiple dataset sizes
   - Edge case handling

2. **Performance Benchmarks**
   - Speed measurements
   - Memory usage
   - Scalability tests
   - Statistical analysis

3. **Stress Tests**
   - Large file processing (100GB+)
   - Extreme load testing
   - Real-time monitoring

4. **Comprehensive Tests**
   - 929,819 texts tested
   - 524M+ characters processed
   - 100% success rate

### Validation Results
- ✅ **100% Reconstruction** - All algorithms
- ✅ **Zero Failures** - All test cases
- ✅ **Perfect Stability** - Deterministic behavior
- ✅ **Universal Coverage** - All languages

---

## SLIDE 29: Comparison Summary

### SOMA vs. Traditional Tokenizers

| Aspect | SOMA | Traditional |
|--------|--------|-------------|
| **Algorithms** | 9 unified | 1 per framework |
| **Training** | None | Required |
| **Reconstruction** | 100% | 90-98% |
| **OOV Handling** | Perfect | Limited |
| **Languages** | Universal | Specific |
| **Deployment** | Immediate | Preparation needed |
| **Determinism** | Guaranteed | Variable |
| **Framework** | Unified | Separate tools |

### Why SOMA?
- **More algorithms** - 9 vs. 1
- **Better accuracy** - 100% vs. 90-98%
- **Faster deployment** - No training vs. required
- **Universal** - Any language vs. specific
- **Unified** - One framework vs. multiple tools

---

## SLIDE 30: Conclusion

### Summary

**SOMA is a complete, production-ready tokenization framework that:**

✅ **Unifies 9 tokenization algorithms** in a single system  
✅ **Guarantees 100% perfect reconstruction** across all algorithms  
✅ **Requires zero training** - immediate deployment  
✅ **Supports universal languages** - any text, any script  
✅ **Provides modern web interface** - React/Next.js dashboard  
✅ **Offers comprehensive API** - RESTful endpoints  
✅ **Includes embedding system** - ML-ready vectors  
✅ **Enables vector search** - Similarity matching  

### Impact

- **Research**: Novel framework for tokenization studies
- **Industry**: Production-ready system for NLP applications
- **Academia**: Complete mathematical foundation and documentation
- **Community**: Open-source framework for text processing

### Future Vision

- Direct integration with major language models
- Performance optimization and GPU support
- Extended algorithm library
- Growing open-source community

---

## SLIDE 31: Contact & Resources

### Project Information

**Author:** Santosh Chavala  
**Email:** chavalasantosh@example.com  
**GitHub:** [@chavalasantosh](https://github.com/chavalasantosh)

### Resources

- **Repository**: GitHub repository
- **Documentation**: Comprehensive guides and papers
- **API Docs**: Swagger UI at `/docs` endpoint
- **Examples**: Multiple usage examples
- **Benchmarks**: Performance test results

### Getting Started

1. Install: `pip install soma`
2. Quick Start: See README.md
3. API Docs: Run server and visit `/docs`
4. Examples: Check `examples/` directory

---

## SLIDE 32: Thank You

### Questions & Discussion

**SOMA - Universal Text Tokenization Framework**

**Key Takeaways:**
- 9 algorithms, 100% reconstruction, zero training
- Production-ready, universal, deterministic
- Complete system with web interface and API

**Thank You!**

---

## APPENDIX: Additional Information

### Mathematical Formulas

**Frontend Digit:**
```
weighted_sum = Σ(i=0 to n-1) (ASCII(char[i]) × (i + 1))
weighted_digit = (weighted_sum - 1) % 9 + 1
hash_value = Σ(i=0 to n-1) (hash_value × 31 + ASCII(char[i]))
hash_digit = hash_value % 10
combined_digit = (weighted_digit × 9 + hash_digit) % 9 + 1
```

**Reconstruction:**
```
reconstructed_text = Σ(i=0 to k-1) token[i].text
where tokens sorted by token[i].index
```

### Performance Details

**Hardware Tested:**
- CPU: Intel Core i5-1245U (6 cores, 12 threads)
- RAM: 16GB DDR4
- OS: Windows 10/11 Pro

**Software:**
- Python: 3.13.7
- FastAPI: Latest
- React: 18
- Next.js: Latest

### File Sizes

**Project:**
- Source Code: ~10MB
- Documentation: ~5MB
- Total: ~15MB (excluding node_modules)

**Demo Version:**
- Cleaned demo: ~0.61MB
- Essential files only
- Ready for sharing

---

## END OF PRESENTATION

**Total Slides: 32 + Appendix**

**Recommended Flow:**
1. Introduction (Slides 1-4)
2. Technical Details (Slides 5-9)
3. Performance (Slides 10-11)
4. Comparison (Slides 12-13)
5. Features (Slides 14-18)
6. Applications (Slides 19-25)
7. Conclusion (Slides 26-32)

**Customization Tips:**
- Adjust slide count based on time available
- Add visual diagrams for architecture
- Include code examples for technical audience
- Add demo screenshots for web interface
- Include performance charts and graphs

