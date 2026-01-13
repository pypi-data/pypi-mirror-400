# Dependencies Analysis

## Overview
This document analyzes the dependencies used in the SOMA project.

## Python Dependencies

### Core Requirements (`requirements.txt`)

#### Production Dependencies
- **FastAPI** - Web framework for API server
- **uvicorn** - ASGI server for FastAPI
- **pydantic** - Data validation using Python type annotations
- **python-multipart** - Support for form data parsing
- **python-jose** - JWT token handling (optional, for authentication)

#### Optional Dependencies
- **numpy** - Numerical computing (used in embeddings)
- **sentence-transformers** - Semantic embeddings (optional)
- **chromadb** - Vector database (optional)
- **faiss-cpu** - Vector similarity search (optional)
- **weaviate-client** - Weaviate vector database client (optional)

#### Development Dependencies
- **pytest** - Testing framework
- **pytest-cov** - Code coverage for pytest
- **black** - Code formatter
- **flake8** - Linter
- **mypy** - Type checker (recommended)

### Backend Requirements (`backend/requirements.txt`)

Similar to main requirements but may include:
- Backend-specific dependencies
- Additional API dependencies

## Node.js Dependencies (`package.json`)

### Frontend Dependencies
- **Next.js** - React framework
- **React** - UI library
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework

### Build Tools
- **TypeScript compiler**
- **PostCSS** - CSS processing
- **ESLint** - JavaScript/TypeScript linter

## Dependency Management Best Practices

### 1. Version Pinning
- ✅ Use specific versions for production
- ✅ Use version ranges for development tools
- ✅ Lock files (package-lock.json, requirements.txt.lock)

### 2. Security
- ✅ Regular dependency updates
- ✅ Security vulnerability scanning
- ✅ Minimal dependencies (only what's needed)

### 3. Organization
- ✅ Separate production and development dependencies
- ✅ Clear documentation of optional dependencies
- ✅ Environment-specific requirements

## Dependency Audit

### Recommended Actions

1. **Security Audit**
   ```bash
   pip install safety
   safety check
   
   npm audit
   ```

2. **Version Updates**
   - Regular updates to latest stable versions
   - Test after updates
   - Keep changelogs

3. **Dependency Review**
   - Remove unused dependencies
   - Consolidate similar packages
   - Review license compatibility

## Optional Dependencies

Some features require optional dependencies:

### Embeddings
- `sentence-transformers` - For semantic embeddings
- `numpy` - For numerical operations

### Vector Databases
- `chromadb` - ChromaDB support
- `faiss-cpu` - FAISS support
- `weaviate-client` - Weaviate support

### Authentication
- `python-jose[cryptography]` - JWT token handling

## Installation

### Production
```bash
pip install -r requirements.txt
```

### Development
```bash
pip install -r requirements.txt
pip install -e ".[dev]"  # If using extras_require
```

### With Optional Features
```bash
pip install -r requirements.txt
pip install sentence-transformers chromadb
```

## Dependency Issues

### Common Issues

1. **Version Conflicts**
   - Use virtual environments
   - Pin versions for stability
   - Use requirements.txt.lock

2. **Missing Optional Dependencies**
   - Features gracefully degrade
   - Clear error messages
   - Documentation of requirements

3. **Platform-Specific Issues**
   - Some packages may have platform-specific builds
   - Use platform-specific installers when needed

## Recommendations

1. ✅ **Keep dependencies minimal** - Only include what's needed
2. ✅ **Pin production versions** - For stability
3. ✅ **Regular updates** - Security patches and bug fixes
4. ✅ **Document optional deps** - Clear what's needed for which features
5. ✅ **Virtual environments** - Isolate dependencies
6. ✅ **Dependency scanning** - Regular security audits

## Tools for Dependency Management

- **pip** - Python package manager
- **pip-tools** - Dependency resolution and pinning
- **poetry** - Modern Python dependency management (alternative)
- **npm/yarn** - Node.js package managers
- **safety** - Security vulnerability scanner
- **pip-audit** - Security audit tool

