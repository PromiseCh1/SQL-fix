# XAMPP SQL Repair Utility

A safe, one-click tool to fix broken MariaDB in XAMPP – without losing your databases.

Created by **Promise**.

---

## Quick Start

### Option 1: Download and Run (.exe)

1. Go to the **dist** folder in this repository.
2. Download `RepairSQL.exe`.
3. Right-click `RepairSQL.exe` → **Run as administrator**.
4. Click **Auto Detect** or browse to your XAMPP folder.
5. Click **Smart Repair** – done.

No Python installation required.

---

### Option 2: Run from Source (for Developers)

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/RepairSQL.git
   cd RepairSQL
   ```

2. Create a virtual environment (optional):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate   # on Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
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

### For the .exe
- Windows 7 or later.
- No additional software.

### For running from source
- Python 3.12+ with PySide6 and psutil.

---

## Building the .exe yourself

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "RepairSQL" src/main.py
```

The .exe will be in the `dist` folder.

---

## License

MIT – free to use and modify.

---

## Credits

**Author**: Promise  
**GitHub**: [PromiseCH1](https://github.com/PromiseCH1)