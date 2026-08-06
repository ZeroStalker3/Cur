import logging
import os
from pathlib import Path

def load_style():
    base_dir = Path(__file__).parent
    style_path = base_dir / "style.qss"

    if not style_path.exists():
        logging.getLogger(__name__).warning(f"Файл стилей не найден: {style_path}")
        return ""
    
    try:
        with open(style_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logging.getLogger(__name__).error(f"Ошибка загрузки стиля: {e}")
        return ""