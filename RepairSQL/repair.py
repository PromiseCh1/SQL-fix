import os
import shutil
import subprocess
import time
from pathlib import Path
from logger import Logger

class RepairEngine:
    def __init__(self, detector, backup_manager):
        self.detector = detector
        self.backup = backup_manager
        self.logger = Logger().get_logger()
        self.data_path = detector.data_path
        self.backup_mysql = os.path.join(detector.backup_path, "mysql")

    def kill_mysqld(self):
        """Force kill all mysqld.exe processes."""
        self.logger.info("Killing mysqld processes...")
        subprocess.run(["taskkill", "/F", "/IM", "mysqld.exe"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time.sleep(1)

    def verify_system_tables(self, mysql_path):
        required = ["user.frm", "db.frm", "plugin.frm", "servers.frm"]
        missing = []
        for f in required:
            if not os.path.exists(os.path.join(mysql_path, f)):
                missing.append(f)
        return missing

    def smart_repair(self):
        """Perform the safe repair procedure."""
        if not self.detector.xampp_path:
            raise Exception("XAMPP not detected. Run detection first.")

        # 1. Kill MySQL
        self.kill_mysqld()

        # 2. Backup the entire data folder
        full_backup_dir = self.backup.create_full_backup(self.data_path)
        self.logger.info(f"Full backup saved to: {full_backup_dir}")

        # 3. Replace system db
        mysql_target = os.path.join(self.data_path, "mysql")
        if os.path.exists(mysql_target):
            # Backup current system db before overwriting
            sys_backup = self.backup.backup_system_db(self.data_path)
            self.logger.info(f"System database backed up to: {sys_backup}")
            shutil.rmtree(mysql_target)

        # Ensure backup mysql exists
        if not os.path.exists(self.backup_mysql):
            raise Exception("Backup mysql folder not found.")

        shutil.copytree(self.backup_mysql, mysql_target)
        self.logger.info("System database replaced from backup.")

        # 4. Verify system tables
        missing = self.verify_system_tables(mysql_target)
        if missing:
            self.logger.error(f"Verification failed. Missing: {missing}")
            # Rollback: restore full backup
            shutil.rmtree(self.data_path)
            shutil.copytree(full_backup_dir, self.data_path)
            raise Exception("Repair failed – restored previous backup.")
        self.logger.info("Verification passed.")

        # 5. Ensure performance_schema and phpmyadmin exist (optional)
        # XAMPP backup may not contain these; skip.

        # 6. Delete temporary files
        for f in ["ibtmp1", "mysql.pid", "aria_log_control"]:
            fp = os.path.join(self.data_path, f)
            if os.path.exists(fp):
                os.remove(fp)
                self.logger.info(f"Removed {f}")

        self.logger.info("Smart repair completed successfully.")
        return full_backup_dir

    def attempt_start(self):
        """Try to start MySQL via net start or manually."""
        try:
            subprocess.run(["net", "start", "mysql"], capture_output=True, shell=True)
        except:
            pass