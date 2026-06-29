import os
import subprocess
import platform
import socket
from pathlib import Path

from src.logger import Logger   # <-- absolute import

class Diagnostics:
    def __init__(self, detector):
        self.detector = detector
        self.logger = Logger().get_logger()

    def run_all(self, output_dir=None):
        if output_dir is None:
            output_dir = Path.home() / "Desktop" / "RepairDiagnostics"
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {
            "system": self._system_info(),
            "xampp": self._xampp_info(),
            "mysql_errors": self._mysql_error_log(),
            "file_tree": self._file_tree(),
            "processes": self._process_list(),
            "network": self._network_info(),
            "environment": self._env_vars()
        }

        for name, content in results.items():
            (output_dir / f"{name}.txt").write_text(content, encoding="utf-8")

        self.logger.info(f"Diagnostics saved to {output_dir}")
        return output_dir

    def _system_info(self):
        info = ["System Information", "=" * 40]
        info.append(f"OS: {platform.system()} {platform.release()} {platform.version()}")
        info.append(f"Machine: {platform.machine()}")
        info.append(f"Processor: {platform.processor()}")
        info.append(f"Hostname: {socket.gethostname()}")
        info.append(f"Python Version: {platform.python_version()}")
        return "\n".join(info)

    def _xampp_info(self):
        d = self.detector
        lines = ["XAMPP Detection", "=" * 40]
        if d.xampp_path:
            lines.append(f"XAMPP Root: {d.xampp_path}")
            lines.append(f"MySQL Path: {d.mysql_path}")
            lines.append(f"Data Path: {d.data_path}")
            lines.append(f"Backup Path: {d.backup_path}")
            lines.append(f"mysqld.exe: {d.mysqld_path}")
            for p in [d.xampp_path, d.mysql_path, d.data_path, d.backup_path, d.mysqld_path]:
                lines.append(f"  - {p} exists: {os.path.exists(p)}")
        else:
            lines.append("XAMPP not detected.")
        return "\n".join(lines)

    def _mysql_error_log(self):
        if self.detector.data_path:
            log_path = Path(self.detector.data_path) / "mysql_error.log"
            if log_path.exists():
                return log_path.read_text(encoding="utf-8", errors="ignore")
        return "No error log found."

    def _file_tree(self):
        if not self.detector.data_path:
            return "No data path."
        try:
            result = subprocess.run(
                ["tree", self.detector.data_path, "/F"],
                capture_output=True, text=True, shell=True
            )
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