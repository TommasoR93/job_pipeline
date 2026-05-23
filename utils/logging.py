from config.config import load_conf
import logging
from pathlib import Path

conf = load_conf()

log_conf = conf.get("LOGGING", "").get("log_file", "")

def create_logger():
    logger = logging.getLogger(__name__)
    #file handler
    log_path = Path(__file__).resolve().parents[1]/log_conf
    file_handler = logging.FileHandler(log_path)
    logger.addHandler(file_handler)
    #level
    level_str = conf.get("LOGGING", "").get("level", "")
    level = getattr(logging, level_str.upper(), logging.INFO)
    logger.setLevel(level)
    #formatter
    formatter = conf.get("LOGGING", "").get("formatter", "")
    formatter_str = logging.Formatter(formatter)
    file_handler.setFormatter(formatter_str)
    return logger
