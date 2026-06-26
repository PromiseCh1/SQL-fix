import sys
from PySide6.QtWidgets import QApplication
from gui import RepairGUI

def main():
    app = QApplication(sys.argv)
    window = RepairGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()