import os
from typing import List, Generator, Callable
from functools import reduce
from core.models import Track
from core.fp_utils import safe_io, Result

# Supported audio formats
AUDIO_EXTENSIONS = ('.mp3', '.wav', '.ogg', '.flac')

# --- 1. RECURSION ---
def find_audio_files_recursive(folder_path: str) -> List[str]:
    """
    FP Concept: Recursion.
    Recursively scans nested directories to extract audio paths without iterative loop stacks.
    """
    if not os.path.exists(folder_path):
        return []

    entries = os.listdir(folder_path)

    def scan_entries(idx: int) -> List[str]:
        if idx >= len(entries):
            return []
        
        full_path = os.path.join(folder_path, entries[idx])
        if os.path.isdir(full_path):
            return find_audio_files_recursive(full_path) + scan_entries(idx + 1)
        elif full_path.lower().endswith(AUDIO_EXTENSIONS):
            return [full_path] + scan_entries(idx + 1)
        else:
            return scan_entries(idx + 1)

    return scan_entries(0)


# --- 2. LAZY EVALUATION (Generators) ---
def stream_audio_tracks(file_paths: List[str]) -> Generator[Track, None, None]:
    """
    FP Concept: Lazy Evaluation.
    Processes audio files lazily on demand using Python generators, avoiding full memory loads.
    """
    for path in file_paths:
        res = load_track_metadata(path)
        if res.is_ok():
            yield res.unwrap()


@safe_io
def load_track_metadata(filepath: str) -> Track:
    """Safe metadata reader returning a Result Monad."""
    filename = os.path.basename(filepath)
    title_part = os.path.splitext(filename)[0]
    
    # Simple split heuristic for "Artist - Title" format
    if " - " in title_part:
        artist, title = title_part.split(" - ", 1)
    else:
        artist, title = "Unknown Artist", title_part

    # Dummy placeholder duration calculation (can be extended with mutagen)
    duration_est = 180.0
    return Track(filepath=filepath, title=title, artist=artist, album="Local Collection", duration_sec=duration_est)


# --- 3. HIGHER-ORDER FUNCTIONS, MAP, FILTER, REDUCE ---
def filter_tracks_by_query(query: str, tracks: List[Track]) -> List[Track]:
    """
    FP Concept: Higher-Order Function (filter) + Lambda.
    """
    q = query.lower().strip()
    if not q:
        return tracks
    return list(filter(lambda t: q in t.title.lower() or q in t.artist.lower() or q in t.album.lower(), tracks))


def transform_track_titles(tracks: List[Track], transform_fn: Callable[[str], str]) -> List[Track]:
    """
    FP Concept: Higher-Order Function (map).
    """
    return list(map(lambda t: t.with_title(transform_fn(t.title)), tracks))


def calculate_total_playlist_duration(tracks: List[Track]) -> float:
    """
    FP Concept: Higher-Order Function (reduce).
    """
    return reduce(lambda total, track: total + track.duration_sec, tracks, 0.0)