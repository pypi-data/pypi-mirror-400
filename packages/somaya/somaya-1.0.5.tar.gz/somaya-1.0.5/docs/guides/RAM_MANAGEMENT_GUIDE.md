# RAM Management Guide for LLM Training

## Current Status
- **Total RAM:** 16,016 MB (15.64 GB)
- **Available RAM:** 2,100 MB (2.05 GB) ⚠️
- **In Use:** 13,916 MB (13.59 GB) - **87% usage**

## Quick Actions to Free RAM

### Step 1: Check What's Using RAM

```powershell
# Check top memory consumers
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 ProcessName, @{Name="RAM(MB)";Expression={[math]::Round($_.WorkingSet/1MB,2)}}
```

### Step 2: Close Applications

**High Priority (Close These):**
- Browser with many tabs (Chrome, Edge, Firefox)
- Visual Studio Code / Other IDEs (if not needed)
- Docker Desktop (if running)
- Virtual machines (if any)
- Video players
- Games
- Other development tools

**Medium Priority:**
- Slack / Teams / Discord
- Email clients
- File explorers with many windows
- PDF readers

**Low Priority (Keep These):**
- System processes
- Antivirus (unless you can pause scans)
- Essential background services

### Step 3: Windows Optimizations

1. **Disable Startup Programs:**
   - Press `Win + R`, type `msconfig`, press Enter
   - Go to "Startup" tab
   - Uncheck unnecessary programs
   - Restart if needed

2. **Clear Browser Cache:**
   - Chrome: Settings > Privacy > Clear browsing data
   - Edge: Settings > Privacy > Clear browsing data

3. **Disable Background Apps:**
   - Settings > Privacy > Background apps
   - Turn off apps you don't need

4. **Set Performance Mode:**
   - Settings > System > Power & battery
   - Set to "Best performance"

### Step 4: Verify Free RAM

```powershell
# Check available RAM
Get-CimInstance Win32_OperatingSystem | Select-Object @{Name="TotalRAM(GB)";Expression={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}}, @{Name="FreeRAM(GB)";Expression={[math]::Round($_.FreePhysicalMemory/1MB,2)}}
```

## Target RAM for Each Model

| Model | Minimum Free RAM | Recommended Free RAM | Your Target |
|-------|-----------------|---------------------|-------------|
| **Showcase SLM** | 2 GB | 4 GB | ✅ You have 2.1 GB (close some apps) |
| **Improved SLM** | 4 GB | 6-8 GB | ⚠️ Need to free 2-4 GB more |
| **Full GPT-Style** | 8 GB | 10-12 GB | ⚠️ Need to free 6-8 GB more |
| **CG-SLM** | 2 GB | 4 GB | ✅ You have 2.1 GB (close some apps) |

## Quick Script to Monitor RAM

Save this as `check_ram.py`:

```python
import psutil
ram = psutil.virtual_memory()
print(f"Total RAM: {ram.total / (1024**3):.2f} GB")
print(f"Available: {ram.available / (1024**3):.2f} GB")
print(f"Used: {ram.used / (1024**3):.2f} GB ({ram.percent}%)")
print()
if ram.available / (1024**3) >= 8:
    print("✅ Ready for Full GPT-Style training")
elif ram.available / (1024**3) >= 4:
    print("✅ Ready for Improved SLM training")
elif ram.available / (1024**3) >= 2:
    print("⚠️  Ready for Showcase SLM (close more apps for better performance)")
else:
    print("❌ Need to free more RAM")
```

Run: `python check_ram.py`

## Before Training Checklist

- [ ] Close browser (or at least most tabs)
- [ ] Close unnecessary applications
- [ ] Check available RAM (should be 4+ GB for Improved SLM)
- [ ] Close other development tools
- [ ] Pause antivirus scans (if safe)
- [ ] Set Windows to Performance mode
- [ ] Verify with `check_ram.py` or PowerShell command

## During Training

- Keep Task Manager open (Ctrl+Shift+Esc)
- Monitor RAM usage
- If RAM gets too low, training may slow down or fail
- Close more apps if needed

## After Training

- You can reopen applications
- Model will be saved to disk
- Training only uses RAM during the process

---

**Quick Command to Check RAM:**
```powershell
Get-CimInstance Win32_OperatingSystem | Select-Object @{Name="FreeRAM(GB)";Expression={[math]::Round($_.FreePhysicalMemory/1MB,2)}}
```

**Target:** At least 4 GB free for Improved SLM, 2 GB minimum for Showcase SLM.
