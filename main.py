import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import ViolationDatabaseApp
from config_logging import setup_logging

def load_stylesheet(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def main():
    setup_logging()
    
    app = QApplication(sys.argv)

    style = load_stylesheet("styles/style.qss")
    app.setStyleSheet(style)
    
    window = ViolationDatabaseApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
