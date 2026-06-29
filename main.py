import sys
import os
import ctypes
from pathlib import Path

# ---- Add src to Python path ----
sys.path.insert(0, str(Path(__file__).parent / "src"))

# ---- UAC Elevation ----
def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

# ---- Import GUI ----
from gui import RepairGUI   # since src is in path
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = RepairGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()