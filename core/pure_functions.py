import math

def format_time(seconds: float) -> str:
    """
    FP Concept: Pure Function.
    Deterministic: Depends solely on input argument 'seconds', produces no side effects.
    """
    if math.isnan(seconds) or seconds < 0:
        return "00:00"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def calculate_progress(current_sec: float, total_sec: float) -> int:
    """
    FP Concept: Pure Function.
    Calculates percentage (0-100) for slider progress.
    """
    if total_sec <= 0:
        return 0
    return min(100, max(0, int((current_sec / total_sec) * 100)))


def normalize_volume(volume_percent: int) -> float:
    """
    FP Concept: Pure Function.
    Maps slider integer (0-100) to float (0.0-1.0).
    """
    return max(0.0, min(1.0, volume_percent / 100.0))