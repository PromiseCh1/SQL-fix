import os
import subprocess
import winreg
from pathlib import Path

class XAMPPDetector:
    def __init__(self):
        self.xampp_path = None
        self.mysql_path = None
        self.data_path = None
        self.backup_path = None
        self.mysqld_path = None

    def detect(self):
        """Search common locations for XAMPP."""
        possible_roots = [f"{d}:\\xampp" for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
        # Also search registry
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall") as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    subkey = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey) as sk:
                        try:
                            display = winreg.QueryValueEx(sk, "DisplayName")[0]
                            if "xampp" in display.lower():
                                install_dir = winreg.QueryValueEx(sk, "InstallLocation")[0]
                                if install_dir and os.path.exists(install_dir):
                                    possible_roots.append(install_dir)
                        except:
                            pass
        except:
            pass

        for root in set(possible_roots):
            if self._validate_xampp(root):
                self.xampp_path = root
                self.mysql_path = os.path.join(root, "mysql")
                self.data_path = os.path.join(self.mysql_path, "data")
                self.backup_path = os.path.join(self.mysql_path, "backup")
                self.mysqld_path = os.path.join(self.mysql_path, "bin", "mysqld.exe")
                return True
        return False

    def _validate_xampp(self, path):
        required = [
            os.path.join(path, "mysql", "bin", "mysqld.exe"),
            os.path.join(path, "mysql", "data"),
            os.path.join(path, "mysql", "backup")
        ]
        return all(os.path.exists(p) for p in required)

    def set_manual(self, path):
        if self._validate_xampp(path):
            self.xampp_path = path
            self.mysql_path = os.path.join(path, "mysql")
            self.data_path = os.path.join(self.mysql_path, "data")
            self.backup_path = os.path.join(self.mysql_path, "backup")
            self.mysqld_path = os.path.join(self.mysql_path, "bin", "mysqld.exe")
            return True
        return False

    def get_info(self):
        if not self.xampp_path:
            return None
        return {
            "xampp": self.xampp_path,
            "mysql": self.mysql_path,
            "data": self.data_path,
            "backup": self.backup_path,
            "mysqld": self.mysqld_path,
        }