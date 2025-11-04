# 🎯 INSTALLATION & FIRST RUN GUIDE

## For Windows Users (Easiest Method)

### Option 1: Automated Setup (Recommended)

1. **Double-click `setup.bat`**

   - Installs all dependencies automatically
   - Runs tests to verify installation
   - Takes 1-2 minutes

2. **Double-click `run.bat`**
   - Launches the application
   - No command line needed!

### Option 2: Manual Setup

1. **Open PowerShell in this folder**

   - Right-click folder → "Open in Terminal"

2. **Install dependencies:**

   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```powershell
   python app.py
   ```

---

## First Time Setup

### Prerequisites

- **Python 3.8 or higher** (3.10+ recommended)

  - Download from: https://python.org/downloads
  - ✓ Check "Add Python to PATH" during installation

- **pip** (included with Python)
  - Verify: `python -m pip --version`

### Verify Installation

After running setup.bat, you should see:

```
✓ Python found!
✓ Installing PySide6...
✓ Installing pytest...
✓ All tests passed!
✓ Setup Complete!
```

---

## 🚀 Running the Application

### Method 1: Batch File (Windows)

```
Double-click run.bat
```

### Method 2: Command Line

```powershell
python app.py
```

### Method 3: Python Module

```powershell
python -m app
```

---

## 📚 Quick Tutorial

### 1️⃣ Load a Sample (30 seconds)

1. Launch app (run.bat or python app.py)
2. Menu: **Samples** → **Single-Instance: Deadlock (Cycle)**
3. Click **Run Detection** button
4. See results in **Results** tab
5. Check **Graph** tab for visualization

### 2️⃣ Create Custom Scenario (2 minutes)

1. Go to **Input** tab
2. Adjust **Processes** and **Resources** spinners
3. Edit **Resource Types** table (total instances)
4. Edit **Available** vector (currently available)
5. Fill **Allocation** matrix (currently allocated)
6. Fill **Request** matrix (currently requested)
7. Click **Run Detection**

### 3️⃣ Understand Results (1 minute)

- **Results tab:** See algorithm trace and verdict
  - "DEADLOCK DETECTED" or "NO DEADLOCK"
  - Step-by-step algorithm execution
- **Recovery Strategies:** If deadlock detected
  - Minimal process termination options
  - Resource preemption suggestions
- **Graph tab:** Visual representation
  - Red nodes = deadlocked processes
  - Red edges = cycle edges
  - Blue nodes = safe processes

---

## 🧪 Testing the Installation

### Run All Tests

```powershell
pytest tests/ -v
```

Expected output:

```
tests/test_wfg.py::test_wfg_no_deadlock PASSED
tests/test_wfg.py::test_wfg_simple_cycle PASSED
tests/test_wfg.py::test_wfg_three_process_cycle PASSED
tests/test_matrix.py::test_matrix_no_deadlock PASSED
tests/test_matrix.py::test_matrix_with_deadlock PASSED
tests/test_schema.py::test_save_and_load_system_state PASSED
...
================= X passed in Y.YYs =================
```

All tests should **PASS** ✅

---

## 🐛 Troubleshooting

### "Python is not recognized"

**Problem:** Python not in PATH
**Solution:**

1. Reinstall Python
2. Check "Add Python to PATH" option
3. Or manually add to PATH

### "No module named 'PySide6'"

**Problem:** Dependencies not installed
**Solution:**

```powershell
pip install PySide6
```

Or re-run setup.bat

### "Application won't start"

**Check Python version:**

```powershell
python --version
```

Must be 3.8 or higher

**Reinstall dependencies:**

```powershell
pip install --upgrade -r requirements.txt
```

### "Tests fail"

**If 1-2 tests fail:** Application may still work
**If many tests fail:**

1. Check Python version (3.8+)
2. Reinstall: `pip install --force-reinstall -r requirements.txt`
3. Check error messages

### "Import errors in IDE"

**Problem:** IDE doesn't see installed packages
**Solution:**

- Select correct Python interpreter in IDE
- Restart IDE after installing packages
- Create virtual environment (optional)

---

## 📁 What Each File Does

### Main Files

- **app.py** - Main entry point (run this!)
- **models.py** - Data structures and validation
- **requirements.txt** - Python packages needed

### Directories

- **detectors/** - Detection algorithms (WFG, Matrix)
- **io/** - File I/O and sample datasets
- **strategies/** - Recovery strategy generation
- **ui/** - All GUI components (PySide6)
- **tests/** - Unit tests for verification

### Documentation

- **README.md** - Complete documentation (theory, usage)
- **QUICKSTART.md** - Get started in 3 steps
- **PROJECT_SUMMARY.md** - Implementation overview
- **INSTALL.md** - This file

### Utilities

- **setup.bat** - Automated installation (Windows)
- **run.bat** - Quick launcher (Windows)
- **example_deadlock.json** - Sample data file
- **.gitignore** - Version control exclusions

---

## 🎓 For Students

### Before Class Demo

1. Run setup.bat (the day before)
2. Test with: python app.py
3. Try all samples to understand features
4. Read README.md theory section

### For Assignment Submission

Include:

1. This entire folder (source code)
2. Screenshots of:
   - Deadlock detection result
   - Graph visualization
   - Recovery strategies
3. Report explaining:
   - How algorithms work
   - Sample scenarios you tested
   - Observations and conclusions

### For Lab Practice

1. Start with samples (understand behavior)
2. Modify samples slightly (experiment)
3. Create custom scenarios (apply knowledge)
4. Compare WFG vs Matrix modes
5. Analyze recovery strategies

---

## 🔧 Advanced Options

### Create Standalone Executable

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --name DeadlockDetective app.py
```

Output: `dist/DeadlockDetective.exe`

### Use Virtual Environment (Recommended for development)

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Custom Python Path

If you have multiple Python versions:

```powershell
C:\Python310\python.exe app.py
```

---

## 📞 Getting Help

### Built-in Help

- **Help → About** - Application info
- **Help → Theory** - OS theory explanation
- **Hover over buttons** - Tooltips (future feature)

### Documentation

- Read **README.md** for complete theory
- Check **QUICKSTART.md** for quick examples
- Review **PROJECT_SUMMARY.md** for overview

### Common Issues

- Input validation errors → Check table values
- Graph not showing → Use Single-Instance mode
- Tests failing → Check Python version

---

## ✅ Installation Checklist

Before presenting/submitting:

- [ ] Python 3.8+ installed
- [ ] Ran setup.bat successfully
- [ ] All tests pass (pytest tests/ -v)
- [ ] App launches (run.bat or python app.py)
- [ ] Loaded and tested all 5 samples
- [ ] Created a custom scenario
- [ ] Graph visualization works
- [ ] Results tab shows traces
- [ ] Recovery strategies appear
- [ ] File save/load works
- [ ] Read README.md theory section

---

## 🎉 You're Ready!

**Installation complete!**

Launch the app:

```
Double-click run.bat
```

Or:

```
python app.py
```

**Next Steps:**

1. Try Sample: Single-Instance Deadlock
2. Read the Results tab trace
3. View the Graph tab visualization
4. Experiment with your own scenarios!

---

**Need more help?** Check README.md or PROJECT_SUMMARY.md

**Happy Deadlock Detecting! 🔍**
