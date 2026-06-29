import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional, Callable

from src.logger import Logger   # <-- absolute import

class RepairEngine:
    def __init__(self, detector, backup_manager):
        self.detector = detector
        self.backup = backup_manager
        self.logger = Logger().get_logger()
        self.data_path: Path = detector.data_path
        self.backup_mysql: Path = detector.backup_path / "mysql"

    def kill_mysqld(self) -> None:
        self.logger.info("Killing mysqld processes...")
        subprocess.run(
            ["taskkill", "/F", "/IM", "mysqld.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True
        )
        time.sleep(1)

    def verify_system_tables(self, mysql_path: Path) -> list[str]:
        required = [
            "user.frm", "db.frm", "plugin.frm", "servers.frm",
            "global_priv.frm", "global_priv.MAD", "global_priv.MAI",
            "columns_priv.frm", "columns_priv.MAD", "columns_priv.MAI",
            "tables_priv.frm", "tables_priv.MAD", "tables_priv.MAI",
            "proxies_priv.frm", "proxies_priv.MAD", "proxies_priv.MAI",
            "roles_mapping.frm", "roles_mapping.MAD", "roles_mapping.MAI",
            "innodb_table_stats.frm", "innodb_table_stats.ibd",
            "innodb_index_stats.frm", "innodb_index_stats.ibd"
        ]
        return [f for f in required if not (mysql_path / f).exists()]

    def verify_mysqld_start(self, data_path: Path, mysqld_path: Path) -> tuple[bool, str]:
        try:
            proc = subprocess.Popen(
                [str(mysqld_path), "--console"],
                cwd=str(data_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True
            )
            time.sleep(5)
            proc.terminate()
            output, _ = proc.communicate(timeout=2)
            if "Fatal error" in output or "Can't open" in output or "Incorrect file format" in output:
                return False, output
            if "ready for connections" in output:
                return True, output
            return True, output
        except Exception as e:
            return False, str(e)

    def smart_repair(self, progress_callback: Optional[Callable[[int, int, str], None]] = None) -> Path:
        if not self.detector.xampp_path:
            raise RuntimeError("XAMPP not detected. Run detection first.")

        if progress_callback:
            progress_callback(1, 5, "Stopping MySQL...")
        self.kill_mysqld()

        if progress_callback:
            progress_callback(2, 10, "Creating full backup...")
        full_backup_dir = self.backup.create_full_backup(self.data_path)
        self.logger.info(f"Full backup saved to: {full_backup_dir}")

        old_data_path = self.data_path.parent / (self.data_path.name + "_old")
        if old_data_path.exists():
            shutil.rmtree(old_data_path)

        if progress_callback:
            progress_callback(3, 30, "Renaming current data...")
        if self.data_path.exists():
            self.data_path.rename(old_data_path)

        if progress_callback:
            progress_callback(4, 40, "Copying system database from backup...")
        self.data_path.mkdir(parents=True, exist_ok=True)
        mysql_target = self.data_path / "mysql"
        shutil.copytree(self.backup_mysql, mysql_target)

        if progress_callback:
            progress_callback(5, 60, "Verifying system tables...")
        missing = self.verify_system_tables(mysql_target)
        if missing:
            self.logger.error(f"Verification failed. Missing: {missing}")
            shutil.rmtree(self.data_path)
            if old_data_path.exists():
                old_data_path.rename(self.data_path)
            raise RuntimeError(f"Repair failed – missing system tables: {', '.join(missing)}")

        if progress_callback:
            progress_callback(6, 70, "Verifying MariaDB start...")
        success, output = self.verify_mysqld_start(self.data_path, self.detector.mysqld_path)
        if not success:
            self.logger.error("MariaDB verification start failed. Rolling back.")
            shutil.rmtree(self.data_path)
            if old_data_path.exists():
                old_data_path.rename(self.data_path)
            raise RuntimeError(f"Repair failed – MariaDB could not start. Output: {output[:200]}...")

        if progress_callback:
            progress_callback(7, 85, "Cleaning temporary files...")
        temp_files = [
            "ibtmp1", "mysql.pid", "aria_log_control",
            "aria_log.00000001", "ib_logfile0", "ib_logfile1"
        ]
        for f in temp_files:
            fp = self.data_path / f
            if fp.exists():
                fp.unlink()
                self.logger.info(f"Removed {f}")

        if old_data_path.exists():
            shutil.rmtree(old_data_path)

        self.logger.info("Smart repair completed successfully.")
        if progress_callback:
            progress_callback(8, 100, "Repair successful!")
        return full_backup_dir

    def attempt_start(self) -> None:
        try:
            subprocess.run(["net", "start", "mysql"], capture_output=True, shell=True)
        except:
            pass