# SOMA Repository Reorganization Plan

## Current Issues Identified
1. **Too many temporary/debug markdown files in root** (30+ files)
2. **Scripts scattered in root** (.bat, .ps1, .sh files)
3. **Large backup files in root** (zip files ~145MB each)
4. **Duplicate directories** (backend, python_code_collection, soma)
5. **Temporary files** (tatus, all_python_output files, etc.)

## Proposed Clean Structure

```
SOMA/
├── README.md                    # Main readme
├── LICENSE
├── requirements.txt
├── setup.py
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── Procfile
├── runtime.txt
├── env.example
│
├── backend/                     # Backend API server
├── frontend/                    # Frontend application
├── soma/                      # Core Python package
├── src/                         # Source code
│
├── docs/                        # All documentation
│   ├── deployment/             # Deployment guides
│   ├── development/            # Development docs
│   ├── archive/                # Old/temporary docs
│   └── api/                    # API documentation
│
├── scripts/                     # All scripts
│   ├── setup/                  # Setup scripts
│   ├── deployment/             # Deployment scripts
│   └── development/            # Development scripts
│
├── tests/                       # Test files
├── examples/                    # Example code
│
├── data/                        # Data files
├── models/                      # Model files (gitignored if large)
├── config/                      # Configuration files
│
└── archive/                     # Old/backup files (gitignored)
    └── backups/                # Backup zip files
```

## Files to Move/Clean

### Documentation (to docs/)
- All BUGS_*.md files → docs/archive/
- All *_DEPLOYMENT_*.md files → docs/deployment/
- All *_FIX*.md files → docs/archive/
- INTEGRATION_*.md → docs/development/
- CLI_USAGE.md → docs/api/
- INSTALLATION.md → docs/development/
- TEAM_ONBOARDING.md → docs/development/
- QUICK_START.md → docs/development/

### Scripts (to scripts/)
- *.bat, *.ps1, *.sh → scripts/setup/ or scripts/deployment/

### Large Files (to archive/)
- *.zip → archive/backups/
- Large .pkl files → models/ (if needed) or archive/
- Large .txt files → archive/

### Temporary Files (delete)
- tatus
- all_python_output_*.txt
- soma_folder_files_paths.txt (if too large)

