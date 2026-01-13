# SOMA Complete Module Package

This zip file contains the complete SOMA (Universal Text Tokenization Framework) module, including:

## 📦 Contents

### Core Components
- **src/**: All Python source code
  - `core/`: Core tokenization engine (core_tokenizer.py, base_tokenizer.py, parallel_tokenizer.py)
  - `servers/`: FastAPI backend servers (main_server.py, api_server.py, lightweight_server.py)
  - `integration/`: Vocabulary adapter for pretrained models (vocabulary_adapter.py)
  - `compression/`: Compression algorithms
  - `cli/`: Command-line interface
  - `utils/`: Utility functions
  - `examples/`: Example usage scripts
  - `tests/`: Test suites
  - `performance/`: Performance testing tools

- **soma/**: Python package directory
  - `soma.py`: Main package module
  - `cli.py`: CLI entry point
  - `__init__.py`: Package initialization

### Backend & API
- **FastAPI Server**: Complete REST API implementation
  - Main server: `src/servers/main_server.py`
  - API endpoints for tokenization, analysis, compression, validation
  - Vocabulary adapter integration endpoints
  - Real-time processing capabilities

### Frontend
- **React/Next.js Frontend**: Modern web interface
  - `frontend/app/`: Next.js app pages
  - `frontend/components/`: React components
  - `frontend/lib/`: API client and utilities
  - `frontend/types/`: TypeScript type definitions
  - Configuration files (package.json, tsconfig.json, tailwind.config.js)

### Documentation
- **docs/**: Comprehensive documentation
  - Project requirements and design documents
  - Vocabulary adapter guides
  - Technical papers
  - Testing guides
  - API documentation

### Examples & Integration
- **examples/**: Integration examples
  - `integration_with_transformers.py`: HuggingFace integration
  - `quick_start_integration.py`: Quick start guide

### Testing & Benchmarks
- **tests/**: Test suites
  - Reconstruction tests
  - Vocabulary adapter backend tests
  - Comprehensive test scripts

- **benchmarks/**: Performance benchmarks
  - Tokenization performance tests
  - Comparison benchmarks

### Scripts & Utilities
- **scripts/**: Helper scripts
  - Server setup scripts
  - Vocabulary adapter test scripts
  - Verification utilities

### Configuration
- **setup.py**: Python package setup
- **requirements.txt**: Python dependencies
- **package.json**: Frontend dependencies (extract zip and run `npm install` in frontend/)
- **README.md**: Main project documentation

### Additional Resources
- **data/**: Sample data files
- **n8n/**: Workflow automation configurations

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Node.js 16+ (for frontend)
- npm or yarn (for frontend)

### Backend Installation

1. Extract this zip file
2. Navigate to the extracted directory
3. Install the Python package:
   ```bash
   pip install -e .
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. (Optional) Install transformers for vocabulary adapter:
   ```bash
   pip install transformers
   ```

### Frontend Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## 🏃 Running the Application

### Backend Server

Start the FastAPI backend:
```bash
python -m uvicorn src.servers.main_server:app --reload
```

Or use the convenience script:
```bash
python QUICK_START_SERVER.bat
```

The API will be available at: `http://localhost:8000`

### Frontend

Start the Next.js frontend (from the frontend directory):
```bash
npm run dev
```

The frontend will be available at: `http://localhost:3000`

## 📚 Key Features

1. **Multi-Perspective Tokenization**: 9 different tokenization strategies
2. **Mathematical Analysis**: Weighted sums, digital roots, hash-based IDs
3. **Perfect Reconstruction**: Lossless tokenization with perfect decode
4. **Vocabulary Adapter**: Bridge SOMA with pretrained transformer models
5. **REST API**: Complete FastAPI backend for integration
6. **Modern Web UI**: React/Next.js frontend dashboard
7. **Comprehensive Documentation**: Extensive guides and technical papers

## 🔗 Integration with Pretrained Models

SOMA can be integrated with HuggingFace transformers using the vocabulary adapter:

```python
from src.core.core_tokenizer import run_once
from src.integration.vocabulary_adapter import quick_convert_soma_to_model_ids

# Tokenize with SOMA
result = run_once("Hello world!", seed=42)
tokens = [rec["text"] for rec in result["word"]["records"]]

# Convert to model vocabulary IDs
model_ids = quick_convert_soma_to_model_ids(tokens, model_name="bert-base-uncased")
```

See `docs/VOCABULARY_ADAPTER_COMPLETE_GUIDE.md` for detailed documentation.

## 📖 Documentation

- Main README: `README.md`
- Vocabulary Adapter Guide: `docs/VOCABULARY_ADAPTER_COMPLETE_GUIDE.md`
- Technical Paper: `docs/VOCABULARY_ADAPTER_TECHNICAL_PAPER.md`
- Testing Guide: `docs/TESTING_VOCABULARY_ADAPTER.md`
- PyPI Publishing: `docs/PYPI_PUBLISHING_CHECKLIST.md`

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Test vocabulary adapter:
```bash
python tests/test_vocabulary_adapter_backend.py
```

## 📝 License

See the main README.md for license information.

## 🤝 Support

For issues, questions, or contributions, refer to the main project documentation.

---

**Note**: This is a complete module package. After extraction, you have everything needed to run SOMA as a standalone application or integrate it into other projects.

