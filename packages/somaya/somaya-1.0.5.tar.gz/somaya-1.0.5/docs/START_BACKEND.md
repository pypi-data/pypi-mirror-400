# 🚀 How to Start the Backend Server

## Quick Start

### Option 1: Using Python Script (Recommended)
```bash
cd scripts/setup
python start_main_server.py
```

### Option 2: Direct Python Command
```bash
cd src/servers
python main_server.py
```

### Option 3: Using Batch File (Windows)
```bash
scripts\setup\start_main_server.bat
```

## What You Should See

When the server starts successfully, you'll see:
```
🚀 Starting SOMA API Server...
📡 Server will be available at: http://localhost:8000
📚 API Documentation at: http://localhost:8000/docs
```

## Verify It's Running

1. Open your browser and go to: http://localhost:8000
2. You should see: `{"message":"SOMA API is running!","version":"1.0.0",...}`
3. Or check the docs at: http://localhost:8000/docs

## Troubleshooting

### If you get "Module not found" errors:
```bash
pip install -r requirements.txt
```

### If port 8000 is already in use:
- Check what's using it: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Mac/Linux)
- Kill the process or change the port in `main_server.py`

### If Python is not found:
- Make sure Python 3.7+ is installed
- Check: `python --version` or `python3 --version`

## Keep the Server Running

**Important**: Keep the terminal window open while using the frontend. Closing it will stop the server.

Once the server is running, go back to your frontend and try uploading your file again!


