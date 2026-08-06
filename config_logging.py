import logging
from pathlib import Path

def setup_logging():
    log_dir = Path(__file__).parent
    log_file = log_dir / "Log_app.log"
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        encoding="utf-8",
        force=True
    )
