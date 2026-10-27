# Spotify Dark Theme QSS Styling Sheet

SPOTIFY_STYLE = """
QMainWindow {
    background-color: #121212;
}

QWidget {
    color: #B3B3B3;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

/* Sidebar */
QFrame#Sidebar {
    background-color: #000000;
    border-right: 1px solid #282828;
}

QLabel#BrandTitle {
    color: #1DB954;
    font-size: 20px;
    font-weight: bold;
}

/* Track Table */
QTableWidget {
    background-color: #121212;
    gridline-color: transparent;
    border: none;
    selection-background-color: #2A2A2A;
    selection-color: #1DB954;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #181818;
}

QHeaderView::section {
    background-color: #121212;
    color: #B3B3B3;
    border: none;
    padding: 8px;
    font-weight: bold;
}

/* Playback Control Bar */
QFrame#ControlBar {
    background-color: #181818;
    border-top: 1px solid #282828;
}

QPushButton {
    background-color: transparent;
    color: #FFFFFF;
    border: none;
    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    color: #1DB954;
}

QPushButton#PlayButton {
    background-color: #1DB954;
    color: #000000;
    border-radius: 18px;
    min-width: 36px;
    min-height: 36px;
}

QPushButton#PlayButton:hover {
    background-color: #1ED760;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 4px;
    background: #535353;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #1DB954;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #FFFFFF;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}

QLineEdit {
    background-color: #242424;
    color: #FFFFFF;
    border-radius: 12px;
    padding: 6px 12px;
    border: 1px solid transparent;
}

QLineEdit:focus {
    border: 1px solid #1DB954;
}
"""