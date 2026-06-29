import sys
import os
import shutil
import traceback
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Absolute imports (src prefix)
from src.detector import XAMPPDetector
from src.backup import BackupManager
from src.repair import RepairEngine
from src.diagnostics import Diagnostics
from src.logger import Logger

class RepairWorker(QThread):
    progress = Signal(int, int, str)
    finished = Signal(bool, str)
    error = Signal(str)

    def __init__(self, detector, backup):
        super().__init__()
        self.detector = detector
        self.backup = backup
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            engine = RepairEngine(self.detector, self.backup)
            def progress_cb(step, percent, msg):
                if self._is_cancelled:
                    raise Exception("Operation cancelled by user.")
                self.progress.emit(step, percent, msg)
            backup_dir = engine.smart_repair(progress_callback=progress_cb)
            self.finished.emit(True, backup_dir)
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit(False, str(e))

class RepairGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Promise's XAMPP SQL Repair Utility")
        self.resize(800, 600)

        self.detector = XAMPPDetector()
        self.backup = BackupManager()
        self.diagnostics = Diagnostics(self.detector)
        self.logger = Logger().get_logger()
        self.worker = None

        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        header = QLabel("Promise's XAMPP SQL Repair Utility")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

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
        btn_repair.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        btn_layout.addWidget(btn_repair)
        layout.addLayout(btn_layout)

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

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Ready")
        layout.addWidget(self.progress_bar)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 9))
        layout.addWidget(self.console)

        self.statusBar().showMessage("Ready")
        self.logger.info("GUI initialized")

    def log_ui(self, message, level="info"):
        colors = {"info": "black", "warning": "orange", "error": "red", "success": "green"}
        color = colors.get(level, "black")
        self.console.append(f'<span style="color:{color}">{message}</span>')

    def update_status_widgets(self):
        if self.detector.xampp_path:
            info = self.detector.get_info()
            self.xampp_label.setText(str(info["xampp"]))
            self.mysql_label.setText(str(info["mysql"]))
            self.data_label.setText(str(info["data"]))
            self.status_indicator.setText("XAMPP detected")
            self.status_indicator.setStyleSheet("color: green;")
            try:
                import subprocess
                result = subprocess.run([str(info["mysqld"]), "--version"], capture_output=True, text=True)
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
            self.log_ui(f"XAMPP found at: {self.detector.xampp_path}", "success")
            self.update_status_widgets()
        else:
            self.log_ui("XAMPP not found. Please use manual selection.", "error")

    def manual_select(self):
        path = QFileDialog.getExistingDirectory(self, "Select XAMPP Root")
        if path:
            if self.detector.set_manual(path):
                self.log_ui(f"XAMPP set manually: {path}", "success")
                self.update_status_widgets()
            else:
                self.log_ui("Invalid XAMPP folder. Missing mysql/bin/mysqld.exe or data/backup.", "error")

    def run_diagnostics(self):
        if not self.detector.xampp_path:
            self.log_ui("Please detect XAMPP first.", "error")
            return
        self.log_ui("Running diagnostics...")
        try:
            output_dir = self.diagnostics.run_all()
            self.log_ui(f"Diagnostics saved to {output_dir}", "success")
            QMessageBox.information(self, "Diagnostics", f"Diagnostics completed.\nSaved to: {output_dir}")
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

        self.setCursor(Qt.WaitCursor)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Starting...")
        self.log_ui("Starting Smart Repair...")
        self.statusBar().showMessage("Repair in progress...")

        self.worker = RepairWorker(self.detector, self.backup)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.repair_finished)
        self.worker.error.connect(self.repair_error)
        self.worker.start()

    def update_progress(self, step, percent, msg):
        self.progress_bar.setValue(percent)
        self.progress_bar.setFormat(msg)
        self.log_ui(f"[{step}] {msg}")

    def repair_finished(self, success, message):
        self.setCursor(Qt.ArrowCursor)
        self.progress_bar.setFormat("Done" if success else "Failed")
        if success:
            self.log_ui(f"Repair completed. Backup saved to: {message}", "success")
            self.statusBar().showMessage("Repair successful")
            QMessageBox.information(self, "Repair", f"Repair completed successfully.\nBackup: {message}")
        else:
            self.log_ui(f"Repair failed: {message}", "error")
            self.statusBar().showMessage("Repair failed")
            QMessageBox.critical(self, "Repair Failed", f"An error occurred:\n\n{message}")
        self.worker = None

    def repair_error(self, error_msg):
        self.log_ui(f"Error: {error_msg}", "error")

    def backup_action(self):
        if not self.detector.data_path:
            self.log_ui("No data path detected.", "error")
            return
        try:
            backup_dir = self.backup.create_full_backup(self.detector.data_path)
            self.log_ui(f"Full backup saved to: {backup_dir}", "success")
            QMessageBox.information(self, "Backup", f"Backup completed.\nSaved to: {backup_dir}")
        except Exception as e:
            self.log_ui(f"Backup failed: {e}", "error")

    def restore_action(self):
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
                    old_data = self.backup.safe_restore_full(backup_path, self.detector.data_path)
                    self.log_ui(f"Restored backup: {item}", "success")
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
            import zipfile
            zip_path = os.path.join(os.path.expanduser("~"), "Desktop", "RepairLogs.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.dirname(output_dir)))
            self.log_ui(f"Logs zipped to: {zip_path}", "success")
            QMessageBox.information(self, "Logs", f"Logs generated and zipped.\n{zip_path}")
        except Exception as e:
            self.log_ui(f"Log generation error: {e}", "error")