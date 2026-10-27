import os
import pygame
from typing import List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, 
    QSlider, QLineEdit, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt, QTimer

from core.models import Track, PlayerState
from core.pure_functions import format_time, calculate_progress, normalize_volume
from core.playlist_ops import (
    find_audio_files_recursive, stream_audio_tracks, 
    filter_tracks_by_query, calculate_total_playlist_duration
)
from core.fp_utils import safe_io
from ui.styles import SPOTIFY_STYLE


class SpotifyOfflineWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Player by Anin-Nindi-Karina")
        self.resize(1000, 650)
        self.setStyleSheet(SPOTIFY_STYLE)

        # Initialize Pygame audio engine
        pygame.mixer.init()

        # State management (Immutable state pattern applied)
        self.state = PlayerState()
        self.all_tracks: List[Track] = []
        self.displayed_tracks: List[Track] = []

        # UI Setup
        self._init_ui()

        # Playback Timer for UI Progress updates
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self._on_timer_tick)
        self.timer.start()

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Upper Content Layout (Sidebar + Main Area)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)

        # 1. Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        
        brand_label = QLabel("Music Player")
        brand_label.setObjectName("BrandTitle")
        sidebar_layout.addWidget(brand_label)

        open_folder_btn = QPushButton("📁 Load Folder")
        open_folder_btn.clicked.connect(self._handle_open_folder)
        sidebar_layout.addWidget(open_folder_btn)

        sidebar_layout.addStretch()
        
        self.total_duration_label = QLabel("Total: 00:00")
        sidebar_layout.addWidget(self.total_duration_label)

        content_layout.addWidget(sidebar)

        # 2. Main Content Area
        main_content = QWidget()
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setContentsMargins(20, 20, 20, 20)

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search by title, artist, or album...")
        self.search_bar.textChanged.connect(self._handle_search)
        main_content_layout.addWidget(self.search_bar)

        # Track List Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Title", "Artist", "Album", "Duration"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self._handle_track_double_click)
        main_content_layout.addWidget(self.table)

        content_layout.addWidget(main_content)
        main_layout.addLayout(content_layout)

        # 3. Bottom Player Bar
        control_bar = QFrame()
        control_bar.setObjectName("ControlBar")
        control_bar.setFixedHeight(90)
        control_layout = QHBoxLayout(control_bar)
        control_layout.setContentsMargins(20, 10, 20, 10)

        # Now Playing Track Info
        self.now_playing_label = QLabel("No track playing")
        self.now_playing_label.setFixedWidth(220)
        control_layout.addWidget(self.now_playing_label)

        # Playback Controls Center
        center_control_layout = QVBoxLayout()
        
        btn_box = QHBoxLayout()
        btn_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.clicked.connect(self._handle_prev)
        self.play_btn = QPushButton("▶")
        self.play_btn.setObjectName("PlayButton")
        self.play_btn.clicked.connect(self._handle_play_pause)
        self.next_btn = QPushButton("⏭")
        self.next_btn.clicked.connect(self._handle_next)

        btn_box.addWidget(self.prev_btn)
        btn_box.addWidget(self.play_btn)
        btn_box.addWidget(self.next_btn)

        # Seek Bar & Time Labels
        time_box = QHBoxLayout()
        self.time_current_label = QLabel("00:00")
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 100)
        self.time_total_label = QLabel("00:00")

        time_box.addWidget(self.time_current_label)
        time_box.addWidget(self.seek_slider)
        time_box.addWidget(self.time_total_label)

        center_control_layout.addLayout(btn_box)
        center_control_layout.addLayout(time_box)
        control_layout.addLayout(center_control_layout)

        # Volume Slider
        vol_box = QHBoxLayout()
        vol_label = QLabel("🔊")
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(70)
        self.vol_slider.setFixedWidth(100)
        self.vol_slider.valueChanged.connect(self._handle_volume_change)

        vol_box.addWidget(vol_label)
        vol_box.addWidget(self.vol_slider)
        control_layout.addLayout(vol_box)

        main_layout.addWidget(control_bar)

    # --- Event Handlers & Functional Binding ---
    def _handle_open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Music Directory")
        if folder:
            # 1. Recursive file search (Recursion)
            paths = find_audio_files_recursive(folder)
            
            # 2. Generator loading (Lazy Evaluation)
            self.all_tracks = list(stream_audio_tracks(paths))
            self.displayed_tracks = self.all_tracks.copy()
            
            # Update UI
            self._render_table(self.displayed_tracks)
            total_sec = calculate_total_playlist_duration(self.all_tracks)
            self.total_duration_label.setText(f"Total: {format_time(total_sec)}")

    def _handle_search(self, text: str):
        # Higher-Order Function filtering
        self.displayed_tracks = filter_tracks_by_query(text, self.all_tracks)
        self._render_table(self.displayed_tracks)

    def _render_table(self, tracks: List[Track]):
        self.table.setRowCount(len(tracks))
        for row, track in enumerate(tracks):
            self.table.setItem(row, 0, QTableWidgetItem(track.title))
            self.table.setItem(row, 1, QTableWidgetItem(track.artist))
            self.table.setItem(row, 2, QTableWidgetItem(track.album))
            self.table.setItem(row, 3, QTableWidgetItem(format_time(track.duration_sec)))

    def _handle_track_double_click(self):
        selected_row = self.table.currentRow()
        if 0 <= selected_row < len(self.displayed_tracks):
            track = self.displayed_tracks[selected_row]
            self._play_track(track)

    @safe_io
    def _play_audio_file(self, filepath: str):
        """Side-effectful audio loading wrapped with safe_io Result monad."""
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()

    def _play_track(self, track: Track):
        res = self._play_audio_file(track.filepath)
        if res.is_ok():
            # Functional state replacement
            self.state = PlayerState(
                current_track=track,
                is_playing=True,
                volume=normalize_volume(self.vol_slider.value()),
                position_sec=0.0
            )
            self.play_btn.setText("⏸")
            self.now_playing_label.setText(f"{track.title}\n{track.artist}")
            self.time_total_label.setText(format_time(track.duration_sec))

    def _handle_play_pause(self):
        if not self.state.current_track:
            if self.displayed_tracks:
                self._play_track(self.displayed_tracks[0])
            return

        if self.state.is_playing:
            pygame.mixer.music.pause()
            self.state = PlayerState(
                current_track=self.state.current_track,
                is_playing=False,
                volume=self.state.volume
            )
            self.play_btn.setText("▶")
        else:
            pygame.mixer.music.unpause()
            self.state = PlayerState(
                current_track=self.state.current_track,
                is_playing=True,
                volume=self.state.volume
            )
            self.play_btn.setText("⏸")

    def _handle_next(self):
        if not self.state.current_track or not self.displayed_tracks:
            return
        idx = self.displayed_tracks.index(self.state.current_track)
        next_idx = (idx + 1) % len(self.displayed_tracks)
        self._play_track(self.displayed_tracks[next_idx])

    def _handle_prev(self):
        if not self.state.current_track or not self.displayed_tracks:
            return
        idx = self.displayed_tracks.index(self.state.current_track)
        prev_idx = (idx - 1) % len(self.displayed_tracks)
        self._play_track(self.displayed_tracks[prev_idx])

    def _handle_volume_change(self, val: int):
        vol = normalize_volume(val)  # Pure function mapping
        pygame.mixer.music.set_volume(vol)
        self.state = PlayerState(
            current_track=self.state.current_track,
            is_playing=self.state.is_playing,
            volume=vol
        )

    def _on_timer_tick(self):
        if self.state.is_playing and pygame.mixer.music.get_busy():
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms >= 0:
                pos_sec = pos_ms / 1000.0
                total_sec = self.state.current_track.duration_sec if self.state.current_track else 1.0
                
                # Pure calculations
                prog = calculate_progress(pos_sec, total_sec)
                self.time_current_label.setText(format_time(pos_sec))
                self.seek_slider.setValue(prog)