import logging
from pathlib import Path
from datetime import datetime

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger()
        return cls._instance

    def _init_logger(self):
        self.logger = logging.getLogger("RepairSQL")
        if self.logger.handlers:
            return

        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        self.logger.addHandler(console)

        log_dir = Path.home() / "Documents" / "RepairSQL_Logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"repair_{datetime.now().strftime('%Y%m%d')}.log"
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def get_logger(self):
        return self.logger