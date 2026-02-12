import os

def load_style():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    style_path = os.path.join(base_dir, "style.qss")

    with open(style_path, "r", encoding="utf-8") as f:
        return f.read()