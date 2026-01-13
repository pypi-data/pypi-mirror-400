# Welcome to SOMA - Team Onboarding Guide

Welcome to the SOMA project! This guide will help you get started quickly.

## 🚀 Quick Start (5 Minutes)

### Step 1: Get the Code

**Option A: Using Git (Recommended)**
```bash
git clone https://github.com/chavalasantosh/SOMA.git
cd SOMA
git checkout backup
```

**Option B: Download ZIP**
1. Go to: https://github.com/chavalasantosh/SOMA
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Open terminal/command prompt in the extracted folder

### Step 2: Setup Backend (Python)

**On Windows:**
```powershell
.\setup.bat
```

**On Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- ✅ Check if Python is installed
- ✅ Create a virtual environment
- ✅ Install all Python dependencies
- ✅ Verify backend setup

### Step 3: Setup Frontend (Node.js)

**Navigate to frontend folder:**
```bash
cd frontend
```

**Install dependencies:**
```bash
npm install
```

**Go back to root:**
```bash
cd ..
```

### Step 4: Start Backend Server

**On Windows:**
```powershell
.\run.bat
```

**On Linux/Mac:**
```bash
./run.sh
```

**Or use Python directly:**
```bash
python start.py
```

The backend will start on **http://localhost:8000**

### Step 5: Start Frontend (in a new terminal)

**Navigate to frontend:**
```bash
cd frontend
```

**Start development server:**
```bash
npm run dev
```

The frontend will start on **http://localhost:3000**

### Step 6: Access the Application

Open your browser:
- **Frontend (Web UI)**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000

🎉 **You're all set!**

---

## 📋 Prerequisites

Before you start, make sure you have:

- **Python 3.11 or higher** (for Backend)
  - Check: `python --version` or `python3 --version`
  - Download: https://www.python.org/downloads/
  
- **Node.js 18+ and npm** (for Frontend)
  - Check: `node --version` and `npm --version`
  - Download: https://nodejs.org/
  
- **Git** (optional, for cloning)
  - Download: https://git-scm.com/downloads

- **4GB RAM minimum** (8GB recommended)

- **2GB free disk space**

---

## 🛠️ Detailed Setup Instructions

### Windows Setup

1. **Open PowerShell or Command Prompt**
   - Press `Win + X` → Select "Windows PowerShell" or "Command Prompt"
   - Navigate to the project folder

2. **Setup Backend**
   ```powershell
   .\setup.bat
   ```
   - Note: In PowerShell, you need `.\` before the script name
   - If you get an error, try: `setup.bat` (in Command Prompt)

3. **Verify Backend Installation**
   ```powershell
   python verify_installation.py
   ```
   - Should show all checks passing ✅

4. **Setup Frontend**
   ```powershell
   cd frontend
   npm install
   cd ..
   ```

5. **Start Backend Server** (Terminal 1)
   ```powershell
   .\run.bat
   ```
   - Keep this terminal open

6. **Start Frontend** (Terminal 2 - New Window)
   ```powershell
   cd frontend
   npm run dev
   ```
   - Keep this terminal open

### Linux/Mac Setup

1. **Open Terminal**
   - Linux: `Ctrl + Alt + T`
   - Mac: `Cmd + Space` → Type "Terminal"

2. **Navigate to Project**
   ```bash
   cd /path/to/SOMA
   ```

3. **Make Scripts Executable**
   ```bash
   chmod +x setup.sh run.sh
   ```

4. **Setup Backend**
   ```bash
   ./setup.sh
   ```

5. **Verify Backend Installation**
   ```bash
   python3 verify_installation.py
   ```

6. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

7. **Start Backend Server** (Terminal 1)
   ```bash
   ./run.sh
   ```
   - Keep this terminal open

8. **Start Frontend** (Terminal 2 - New Tab/Window)
   ```bash
   cd frontend
   npm run dev
   ```
   - Keep this terminal open

---

## 🐳 Alternative: Docker Setup

If you have Docker installed, this is the easiest method:

```bash
docker-compose up
```

The server will be available at http://localhost:8000

**Note**: Make sure Docker Desktop is running before using this method.

---

## 📚 What is SOMA?

SOMA is an **Advanced Text Tokenization Framework** with both **Backend API** and **Frontend Web Interface**:

### Backend (Python/FastAPI)
- **Multiple Tokenization Methods**: Word, character, subword, byte-level, grammar-based
- **Semantic Embeddings**: Generate embeddings using multiple strategies
- **RESTful API**: FastAPI-based server with interactive documentation
- **WebSocket Support**: Real-time tokenization and streaming
- **Vector Database Integration**: Support for ChromaDB, FAISS, and Weaviate
- **Training Capabilities**: Train custom semantic models on your data
- **CLI Interface**: Command-line tools for all operations

### Frontend (Next.js/React)
- **Interactive Web UI**: Modern, responsive web interface
- **Real-time Tokenization**: Live processing with instant results
- **File Upload**: Drag & drop support for multiple file types
- **Visual Analytics**: Charts and performance metrics
- **Dark Mode**: System preference detection
- **9 Tokenizer Types**: All tokenization methods available in UI

---

## 🎯 Common Tasks

### Start Backend Server
```bash
# Windows
.\run.bat

# Linux/Mac
./run.sh

# Or directly
python start.py
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Stop Servers
Press `Ctrl + C` in each terminal where servers are running

### Change Backend Port
If port 8000 is already in use:
```bash
PORT=8001 python start.py
```

### Change Frontend Port
If port 3000 is already in use:
```bash
cd frontend
PORT=3001 npm run dev
```

### Build Frontend for Production
```bash
cd frontend
npm run build
npm start
```

### Verify Installation
```bash
python verify_installation.py
```

### Use the CLI
```bash
# Tokenize text
python soma_cli.py tokenize --text "Hello world" --method word

# Train a model
python soma_cli.py train --file corpus.txt --model-path model.pkl

# Generate embeddings
python soma_cli.py embed --text "Hello" --model-path model.pkl
```

---

## ❓ Troubleshooting

### Problem: "Python is not recognized"
**Solution**: 
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal after installation

### Problem: "npm is not recognized" or "node is not recognized"
**Solution**:
- Install Node.js from https://nodejs.org/
- This includes npm automatically
- Restart your terminal after installation
- Verify: `node --version` and `npm --version`

### Problem: "Port 8000 is already in use"
**Solution**:
```bash
PORT=8001 python start.py
```

### Problem: "Dependencies fail to install"
**Solution**:
```bash
# Upgrade pip first
pip install --upgrade pip

# Then try setup again
.\setup.bat  # Windows
./setup.sh   # Linux/Mac
```

### Problem: "Permission denied" (Linux/Mac)
**Solution**:
```bash
chmod +x setup.sh run.sh
```

### Problem: PowerShell says "script not found"
**Solution**: Use `.\` prefix:
```powershell
.\setup.bat
.\run.bat
```

Or use Command Prompt instead of PowerShell.

### Problem: "ModuleNotFoundError" (Backend)
**Solution**:
1. Make sure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Run `python verify_installation.py` to diagnose

### Problem: Frontend won't start or has errors
**Solution**:
1. Make sure you're in the `frontend` directory
2. Delete `node_modules` and `package-lock.json`
3. Reinstall: `npm install`
4. Try: `npm run dev`

### Problem: Frontend can't connect to backend
**Solution**:
1. Make sure backend is running on http://localhost:8000
2. Check backend is accessible: Open http://localhost:8000/docs in browser
3. Verify frontend API configuration in `frontend/lib/api.ts`
4. Check for CORS errors in browser console

---

## 📖 Documentation

- **README.md** - Main project documentation
- **INSTALLATION.md** - Detailed installation guide
- **QUICK_START.md** - Quick reference guide
- **CLI_USAGE.md** - Command-line interface guide
- **API Docs** - Available at http://localhost:8000/docs when server is running

---

## 🔗 Useful Links

- **Repository**: https://github.com/chavalasantosh/SOMA
- **Branch**: `backup`
- **API Documentation**: http://localhost:8000/docs (when server is running)

---

## 💡 Tips

1. **Always use virtual environment**: The setup script creates one automatically
2. **Check Python version**: Must be 3.11 or higher
3. **Read error messages**: They usually tell you exactly what's wrong
4. **Use verification script**: `python verify_installation.py` helps diagnose issues
5. **Keep dependencies updated**: Run `pip install --upgrade pip` regularly

---

## 🆘 Getting Help

If you encounter issues:

1. **Run verification**: `python verify_installation.py`
2. **Check documentation**: See INSTALLATION.md for detailed troubleshooting
3. **Check server logs**: Look at the terminal output for error messages
4. **Verify Python version**: `python --version` should show 3.11+
5. **Check file structure**: Make sure you're in the project root directory

---

## ✅ Verification Checklist

After setup, verify everything works:

### Backend:
- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] All Python dependencies installed
- [ ] `python verify_installation.py` passes all checks
- [ ] Backend server starts without errors
- [ ] Can access http://localhost:8000/docs in browser
- [ ] Can make API requests

### Frontend:
- [ ] Node.js 18+ installed
- [ ] npm installed
- [ ] All frontend dependencies installed (`npm install` completed)
- [ ] Frontend dev server starts without errors
- [ ] Can access http://localhost:3000 in browser
- [ ] Frontend can connect to backend API
- [ ] UI loads and displays correctly

---

## 🎓 Next Steps

Once you have everything running:

1. **Explore the Frontend**: Visit http://localhost:3000 - Try tokenizing some text!
2. **Explore the API**: Visit http://localhost:8000/docs - See all available endpoints
3. **Try the CLI**: Run `python soma_cli.py --help`
4. **Read the docs**: Check README.md and other documentation files
5. **Start coding**: The codebase is ready for development!

## 🏗️ Project Structure

```
SOMA/
├── backend/              # Backend Python code
│   └── src/             # Source code
├── frontend/            # Frontend Next.js application
│   ├── app/            # Next.js app router pages
│   ├── components/     # React components
│   └── lib/           # Utilities and API clients
├── src/                # Core Python modules
├── setup.sh / setup.bat # Backend setup scripts
├── run.sh / run.bat    # Backend run scripts
└── requirements.txt    # Python dependencies
```

---

## 📝 Notes

- The project uses **Git LFS** for large model files (they'll download automatically)
- Some files may take time to download on first clone (large models)
- The server runs on port 8000 by default
- All configuration can be changed via environment variables (see `env.example`)

---

**Welcome to the team! Happy coding! 🚀**

For questions or issues, refer to the documentation or contact the team lead.

