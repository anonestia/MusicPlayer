import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import SpotifyOfflineWindow

def main():
    app = QApplication(sys.argv)
    window = SpotifyOfflineWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()