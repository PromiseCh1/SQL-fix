import sys
import threading
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from detector import XAMPPDetector
from backup import BackupManager
from repair import RepairEngine
from diagnostics import Diagnostics
from logger import Logger

class RepairGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Promise's XAMPP SQL Repair Utility")
        self.resize(800, 600)

        self.detector = XAMPPDetector()
        self.backup = BackupManager()
        self.repair_engine = None
        self.diagnostics = Diagnostics(self.detector)
        self.logger = Logger().get_logger()

        self.init_ui()

    def init_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Header
        header = QLabel("Promise's XAMPP SQL Repair Utility")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Status Frame
        status_frame = QGroupBox("System Status")
        status_layout = QFormLayout()
        self.xampp_label = QLabel("Not detected")
        self.mysql_label = QLabel("Not detected")
        self.version_label = QLabel("Unknown")
        self.data_label = QLabel("Unknown")
        self.status_indicator = QLabel("Unknown")
        self.status_indicator.setStyleSheet("color: gray;")
        status_layout.addRow("XAMPP Location:", self.xampp_label)
        status_layout.addRow("MySQL Path:", self.mysql_label)
        status_layout.addRow("MariaDB Version:", self.version_label)
        status_layout.addRow("Data Folder:", self.data_label)
        status_layout.addRow("Status:", self.status_indicator)
        status_frame.setLayout(status_layout)
        layout.addWidget(status_frame)

        # Buttons (first row)
        btn_layout = QHBoxLayout()
        btn_detect = QPushButton("Auto Detect XAMPP")
        btn_detect.clicked.connect(self.auto_detect)
        btn_layout.addWidget(btn_detect)

        btn_manual = QPushButton("Manual Select XAMPP Folder")
        btn_manual.clicked.connect(self.manual_select)
        btn_layout.addWidget(btn_manual)

        btn_diagnose = QPushButton("Diagnose")
        btn_diagnose.clicked.connect(self.run_diagnostics)
        btn_layout.addWidget(btn_diagnose)

        btn_repair = QPushButton("Smart Repair")
        btn_repair.clicked.connect(self.smart_repair)
        btn_repair.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_layout.addWidget(btn_repair)
        layout.addLayout(btn_layout)

        # Second row
        btn_layout2 = QHBoxLayout()
        btn_backup = QPushButton("Backup Database")
        btn_backup.clicked.connect(self.backup_action)
        btn_layout2.addWidget(btn_backup)

        btn_restore = QPushButton("Restore Database")
        btn_restore.clicked.connect(self.restore_action)
        btn_layout2.addWidget(btn_restore)

        btn_logs = QPushButton("Generate Logs")
        btn_logs.clicked.connect(self.generate_logs)
        btn_layout2.addWidget(btn_logs)

        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.close)
        btn_layout2.addWidget(btn_exit)
        layout.addLayout(btn_layout2)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Console output area
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 9))
        layout.addWidget(self.console)

        # Status bar
        self.statusBar().showMessage("Ready")

        self.logger.info("GUI initialized")

    def log_ui(self, message, level="info"):
        colors = {"info": "black", "warning": "orange", "error": "red"}
        color = colors.get(level, "black")
        self.console.append(f'<span style="color:{color}">{message}</span>')

    def update_status_widgets(self):
        if self.detector.xampp_path:
            info = self.detector.get_info()
            self.xampp_label.setText(info["xampp"])
            self.mysql_label.setText(info["mysql"])
            self.data_label.setText(info["data"])
            self.status_indicator.setText("XAMPP detected")
            self.status_indicator.setStyleSheet("color: green;")
            # Try to get version
            try:
                import subprocess
                result = subprocess.run([info["mysqld"], "--version"], capture_output=True, text=True)
                self.version_label.setText(result.stdout.split()[4] if result.stdout else "Unknown")
            except:
                self.version_label.setText("Unknown")
        else:
            self.xampp_label.setText("Not detected")
            self.mysql_label.setText("Not detected")
            self.version_label.setText("Unknown")
            self.data_label.setText("Unknown")
            self.status_indicator.setText("Not detected")
            self.status_indicator.setStyleSheet("color: red;")

    def auto_detect(self):
        self.log_ui("Running auto-detection...")
        if self.detector.detect():
            self.log_ui(f"XAMPP found at: {self.detector.xampp_path}")
            self.update_status_widgets()
        else:
            self.log_ui("XAMPP not found. Please use manual selection.", "error")

    def manual_select(self):
        path = QFileDialog.getExistingDirectory(self, "Select XAMPP Root")
        if path:
            if self.detector.set_manual(path):
                self.log_ui(f"XAMPP set manually: {path}")
                self.update_status_widgets()
            else:
                self.log_ui("Invalid XAMPP folder. Missing mysql/bin/mysqld.exe or data/backup.", "error")

    def run_diagnostics(self):
        if not self.detector.xampp_path:
            self.log_ui("Please detect XAMPP first.", "error")
            return
        self.log_ui("Running diagnostics...")
        try:
            self.diagnostics.run_all()
            self.log_ui("Diagnostics saved to Desktop/RepairDiagnostics")
            QMessageBox.information(self, "Diagnostics", "Diagnostics completed. Check Desktop/RepairDiagnostics.")
        except Exception as e:
            self.log_ui(f"Diagnostics error: {e}", "error")

    def smart_repair(self):
        if not self.detector.xampp_path:
            self.log_ui("Please detect XAMPP first.", "error")
            return
        reply = QMessageBox.question(self, "Confirm Repair",
                                     "Smart Repair will replace the system database (mysql) with the backup version.\n"
                                     "A full backup of your data folder will be created.\n\n"
                                     "Proceed?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        self.progress.setValue(0)
        self.log_ui("Starting Smart Repair...")

        self.repair_engine = RepairEngine(self.detector, self.backup)

        def thread_func():
            try:
                backup_dir = self.repair_engine.smart_repair()
                self.log_ui(f"Repair completed. Backup saved to: {backup_dir}")
                self.progress.setValue(100)
                self.statusBar().showMessage("Repair successful")
                QMessageBox.information(self, "Repair", f"Repair completed successfully.\nBackup: {backup_dir}")
            except Exception as e:
                self.log_ui(f"Repair failed: {e}", "error")
                self.progress.setValue(0)
                self.statusBar().showMessage("Repair failed")
                QMessageBox.critical(self, "Repair Failed", str(e))

        thread = threading.Thread(target=thread_func)
        thread.daemon = True
        thread.start()

    def backup_action(self):
        if not self.detector.data_path:
            self.log_ui("No data path detected.", "error")
            return
        try:
            backup_dir = self.backup.create_full_backup(self.detector.data_path)
            self.log_ui(f"Full backup saved to: {backup_dir}")
            QMessageBox.information(self, "Backup", f"Backup completed.\nSaved to: {backup_dir}")
        except Exception as e:
            self.log_ui(f"Backup failed: {e}", "error")

    def restore_action(self):
        # Simple restore: select a backup folder
        if not self.detector.data_path:
            self.log_ui("No data path detected.", "error")
            return
        backups = self.backup.list_backups()
        if not backups:
            self.log_ui("No backups found.", "warning")
            return
        item, ok = QInputDialog.getItem(self, "Restore Backup", "Select backup folder:", backups, 0, False)
        if ok and item:
            backup_path = os.path.join(self.backup.base_dir, item)
            reply = QMessageBox.question(self, "Confirm Restore",
                                         f"Restore entire data folder from:\n{backup_path}?\n\nThis will overwrite current data.",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    shutil.rmtree(self.detector.data_path)
                    shutil.copytree(backup_path, self.detector.data_path)
                    self.log_ui(f"Restored backup: {item}")
                    QMessageBox.information(self, "Restore", "Restore completed.")
                except Exception as e:
                    self.log_ui(f"Restore failed: {e}", "error")

    def generate_logs(self):
        if not self.detector.xampp_path:
            self.log_ui("Please detect XAMPP first.", "error")
            return
        self.log_ui("Generating logs...")
        try:
            output_dir = self.diagnostics.run_all()
            # Zip the folder
            import zipfile
            zip_path = os.path.join(os.path.expanduser("~"), "Desktop", "RepairLogs.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.dirname(output_dir)))
            self.log_ui(f"Logs zipped to: {zip_path}")
            QMessageBox.information(self, "Logs", f"Logs generated and zipped.\n{zip_path}")
        except Exception as e:
            self.log_ui(f"Log generation error: {e}", "error")