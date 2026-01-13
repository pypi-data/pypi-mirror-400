# 🎯 WHERE TO LOOK - SOMA Codebase Guide

## 📂 **MAIN DIRECTORIES (Focus Here!)**

### 1. **`backend/`** - Backend API Server (Python/FastAPI)
   - **Main Entry Point:** `backend/src/servers/main_server.py`
   - **Job Manager:** `backend/src/servers/job_manager.py`
   - **Dependencies:** `backend/requirements.txt`
   - **What it does:** Runs the API server that handles code execution, tokenization, embeddings

### 2. **`frontend/`** - Web UI (Next.js/React/TypeScript)
   - **Main Page:** `frontend/app/page.tsx`
   - **Code Editor:** `frontend/components/vscode-editor.tsx`
   - **Terminal:** `frontend/components/interactive-terminal.tsx`
   - **Dependencies:** `frontend/package.json`
   - **What it does:** The web interface users see (editor, terminal, UI)

### 3. **`src/`** - Core Source Code (Python)
   - **Tokenizer:** `src/core/core_tokenizer.py`
   - **Embeddings:** `src/embeddings/embedding_generator.py`
   - **Vector Store:** `src/embeddings/vector_store.py`
   - **Servers:** `src/servers/main_server.py` (same as backend)
   - **What it does:** Core tokenization and embedding logic

---

## 🚀 **RAILWAY DEPLOYMENT (What You Need)**

### Root Directory Files:
- ✅ `Procfile` - Railway startup command
- ✅ `railway.json` - Railway configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `package.json` - Frontend dependencies
- ✅ `runtime.txt` - Python version

### Key Files for Deployment:
1. **Backend:** `backend/src/servers/main_server.py` (starts API server)
2. **Frontend:** `frontend/package.json` (builds Next.js app)
3. **Config:** `railway.json` (Railway settings)

---

## 🔍 **IF YOU NEED TO:**

### Fix Backend Issues:
→ Look in: `backend/src/servers/`
→ Key file: `main_server.py`, `job_manager.py`

### Fix Frontend Issues:
→ Look in: `frontend/components/`
→ Key files: `vscode-editor.tsx`, `interactive-terminal.tsx`, `hooks/useAsyncJob.ts`

### Understand Core Logic:
→ Look in: `src/core/` and `src/embeddings/`
→ Key files: `core_tokenizer.py`, `embedding_generator.py`, `vector_store.py`

### Deploy to Railway:
→ Use: `soma_railway.zip` (already created!)
→ Or check: `railway/` folder for deployment scripts

---

## 📝 **IGNORE THESE (Not Critical):**

- `docs/` - Documentation
- `demo_soma/` - Demo folder
- `*.bat`, `*.sh`, `*.ps1` - Development scripts
- `*.zip` - Old ZIP files
- `*.md` - Documentation files (except README.md)

## ✅ **IMPORTANT DIRECTORIES (Include These!):**

- ✅ `examples/` - **IMPORTANT:** Contains exceptional example code
- ✅ `tests/` - **IMPORTANT:** Contains test files and exceptional code
- ✅ `benchmarks/` - **IMPORTANT:** Contains benchmark scripts

---

## ✅ **SUMMARY:**

**For Railway Deployment:**
1. Backend: `backend/src/servers/main_server.py`
2. Frontend: `frontend/`
3. Config: Root `Procfile`, `railway.json`, `requirements.txt`

**For Development:**
1. Backend code: `backend/src/` or `src/`
2. Frontend code: `frontend/components/`, `frontend/app/`
3. Core logic: `src/core/`, `src/embeddings/`

**That's it! Don't worry about the rest!** 🎯

