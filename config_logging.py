import logging

def setup_logging():
    logging.basicConfig(
        filename="Log_app.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        encoding="utf-8"
    )
