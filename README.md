# XAMPP SQL Repair Utility

A safe, one-click tool to fix broken MariaDB in XAMPP – without losing your databases.

Created by **Promise**.

---

## What it does

- Detects your XAMPP installation automatically.
- Backs up your entire `mysql/data` folder to your desktop.
- Replaces only the corrupted system tables (`mysql` database) with the original backup.
- Preserves all your user databases (WordPress, custom projects, etc.).
- Verifies the repair and rolls back automatically if something fails.
- Generates diagnostic logs for troubleshooting.

---

## How to use

1. Download `RepairSQL.exe` (standalone – no Python required).
2. Run it as Administrator.
3. Click **Auto Detect** or browse to your XAMPP folder.
4. Click **Smart Repair**.
5. Start MariaDB from XAMPP – it should now work.

---

## Requirements

- Windows 7 or later.
- No additional software – the `.exe` is self-contained.

---

## For developers

- Python 3.12+ with PySide6 and psutil.
- Clone the repo and run `pip install -r requirements.txt`, then `python main.py`.

---

## License

MIT – free to use and modify.

---

## Credits

**Author**: Promise  
**GitHub**: [promisech1](https://github.com/promisech1)