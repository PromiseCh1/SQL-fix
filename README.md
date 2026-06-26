# XAMPP SQL Repair Utility

A safe, one-click tool to fix broken MariaDB in XAMPP – without losing your databases.

Created by **Promise**.

---

## Quick Start

### Option 1: Download and Run the .exe (No Python Required)

1. Go to the `dist` folder in this repository.
2. Download `RepairSQL.exe`.
3. Right-click the `.exe` → **Run as administrator**.
4. Click **Auto Detect** or browse to your XAMPP folder.
5. Click **Smart Repair** – done.

> No Python installation required. Works on any Windows 7+ machine.

---

### Option 2: Run from Source (For Developers)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/RepairSQL.git
   cd RepairSQL
   ```

2. **Install Python 3.12 or later** (if not already installed).  
   Download from [python.org](https://python.org) – make sure to check **"Add Python to PATH"** during installation.

3. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate   # on Windows
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```bash
   python src/main.py
   ```

---

## What it does

- Detects your XAMPP installation automatically.
- Backs up your entire `mysql/data` folder to your desktop.
- Replaces only the corrupted system tables (`mysql` database) with the original backup.
- Preserves all your user databases (WordPress, custom projects, etc.).
- Verifies the repair and rolls back automatically if something fails.
- Generates diagnostic logs for troubleshooting.

---

## Requirements

### For the .exe (Option 1)
- Windows 7 or later (64‑bit recommended).
- No additional software – the .exe is self‑contained.

### For running from source (Option 2)
- Python 3.12 or later.
- Dependencies listed in `requirements.txt` (PySide6 and psutil).

---

## Building the .exe yourself (if you want to compile)

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "RepairSQL" src/main.py
```

The .exe will appear in the `dist` folder.

---

## License

MIT – free to use and modify.

---

## Credits

**Author**: Promise  
**GitHub**: [PromiseCH1](https://github.com/PromiseCH1)