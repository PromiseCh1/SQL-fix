import os
import shutil
import datetime
import zipfile
from pathlib import Path

class BackupManager:
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.join(os.path.expanduser("~"), "Desktop", "MariaDB_Backups")
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def create_full_backup(self, data_path, custom_name=None):
        """Create a timestamped full backup of the data folder."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if custom_name:
            folder_name = custom_name
        else:
            folder_name = f"backup_{timestamp}"
        backup_dir = os.path.join(self.base_dir, folder_name)
        os.makedirs(backup_dir, exist_ok=True)

        # Copy entire data folder
        shutil.copytree(data_path, backup_dir, ignore_dangling_symlinks=True, dirs_exist_ok=True)
        return backup_dir

    def backup_system_db(self, data_path):
        """Backup only the mysql system database."""
        mysql_src = os.path.join(data_path, "mysql")
        if not os.path.exists(mysql_src):
            return None
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_dir = os.path.join(self.base_dir, f"system_backup_{timestamp}")
        shutil.copytree(mysql_src, backup_dir)
        return backup_dir

    def restore_system_db(self, backup_path, data_path):
        """Restore mysql system database from a backup."""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        target = os.path.join(data_path, "mysql")
        if os.path.exists(target):
            # Rename existing to keep a fallback
            shutil.move(target, target + "_old")
        shutil.copytree(backup_path, target)
        return True

    def list_backups(self):
        return [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]