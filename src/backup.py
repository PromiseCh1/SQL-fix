import os
import shutil
import datetime
from pathlib import Path

class BackupManager:
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path.home() / "Desktop" / "MariaDB_Backups"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_full_backup(self, data_path, custom_name=None):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder_name = custom_name or f"backup_{timestamp}"
        backup_dir = self.base_dir / folder_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(data_path, backup_dir, dirs_exist_ok=True, ignore_dangling_symlinks=True)
        return backup_dir

    def backup_system_db(self, data_path):
        mysql_src = Path(data_path) / "mysql"
        if not mysql_src.exists():
            return None
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_dir = self.base_dir / f"system_backup_{timestamp}"
        shutil.copytree(mysql_src, backup_dir)
        return backup_dir

    def restore_system_db(self, backup_path, data_path):
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        target = Path(data_path) / "mysql"
        if target.exists():
            target.rename(target.parent / (target.name + "_old"))
        shutil.copytree(backup_path, target)
        return True

    def list_backups(self):
        return [d.name for d in self.base_dir.iterdir() if d.is_dir()]

    def safe_restore_full(self, backup_path, data_path):
        backup_path = Path(backup_path)
        data_path = Path(data_path)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        old_path = data_path.parent / (data_path.name + "_old")
        if old_path.exists():
            shutil.rmtree(old_path)

        if data_path.exists():
            data_path.rename(old_path)

        shutil.copytree(backup_path, data_path)
        return old_path

    def rollback_restore(self, old_path, data_path):
        old_path = Path(old_path)
        data_path = Path(data_path)
        if data_path.exists():
            shutil.rmtree(data_path)
        if old_path.exists():
            old_path.rename(data_path)