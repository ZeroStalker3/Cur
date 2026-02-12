import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import ViolationDatabaseApp
from styles.style_loader import load_style

def main():
    
    app = QApplication(sys.argv)

    app.setStyleSheet(load_style())
    
    window = ViolationDatabaseApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
