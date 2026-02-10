import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import ViolationDatabaseApp


def main():
    app = QApplication(sys.argv)
    window = ViolationDatabaseApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
