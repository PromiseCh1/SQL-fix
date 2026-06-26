import os
import subprocess
import platform
import socket
import datetime
from pathlib import Path
from logger import Logger

class Diagnostics:
    def __init__(self, detector):
        self.detector = detector
        self.logger = Logger().get_logger()

    def run_all(self, output_dir=None):
        if output_dir is None:
            output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "RepairDiagnostics")
        os.makedirs(output_dir, exist_ok=True)

        results = {}
        results["system"] = self._system_info()
        results["xampp"] = self._xampp_info()
        results["mysql_errors"] = self._mysql_error_log()
        results["file_tree"] = self._file_tree()
        results["processes"] = self._process_list()
        results["network"] = self._network_info()
        results["environment"] = self._env_vars()

        # Write to files
        for name, content in results.items():
            with open(os.path.join(output_dir, f"{name}.txt"), "w", encoding="utf-8") as f:
                f.write(content)

        self.logger.info(f"Diagnostics saved to {output_dir}")
        return output_dir

    def _system_info(self):
        info = []
        info.append("System Information")
        info.append("=" * 40)
        info.append(f"OS: {platform.system()} {platform.release()} {platform.version()}")
        info.append(f"Machine: {platform.machine()}")
        info.append(f"Processor: {platform.processor()}")
        info.append(f"Hostname: {socket.gethostname()}")
        info.append(f"Python Version: {platform.python_version()}")
        return "\n".join(info)

    def _xampp_info(self):
        d = self.detector
        info = []
        info.append("XAMPP Detection")
        info.append("=" * 40)
        if d.xampp_path:
            info.append(f"XAMPP Root: {d.xampp_path}")
            info.append(f"MySQL Path: {d.mysql_path}")
            info.append(f"Data Path: {d.data_path}")
            info.append(f"Backup Path: {d.backup_path}")
            info.append(f"mysqld.exe: {d.mysqld_path}")
            # Check existence
            for path in [d.xampp_path, d.mysql_path, d.data_path, d.backup_path, d.mysqld_path]:
                info.append(f"  - {path} exists: {os.path.exists(path)}")
        else:
            info.append("XAMPP not detected.")
        return "\n".join(info)

    def _mysql_error_log(self):
        log_path = os.path.join(self.detector.data_path, "mysql_error.log") if self.detector.data_path else None
        if log_path and os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        return "No error log found."

    def _file_tree(self):
        if not self.detector.data_path:
            return "No data path."
        import subprocess
        try:
            result = subprocess.run(["tree", self.detector.data_path, "/F"], capture_output=True, text=True, shell=True)
            return result.stdout if result.returncode == 0 else "Tree command failed."
        except:
            return "Tree not available."

    def _process_list(self):
        try:
            result = subprocess.run(["tasklist", "/V"], capture_output=True, text=True, shell=True)
            return result.stdout
        except:
            return "Process list not available."

    def _network_info(self):
        try:
            result = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True, shell=True)
            return result.stdout
        except:
            return "Network info not available."

    def _env_vars(self):
        import os
        return "\n".join([f"{k}={v}" for k, v in os.environ.items()])