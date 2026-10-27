from dataclasses import dataclass, replace
from typing import Optional

@dataclass(frozen=True)
class Track:
    """
    Immutable representation of an audio track.
    FP Concept: Immutability (frozen=True prevents state modification after creation).
    """
    filepath: str
    title: str
    artist: str
    album: str
    duration_sec: float

    def with_title(self, new_title: str) -> "Track":
        """Returns a new copy with modified title instead of mutating in-place."""
        return replace(self, title=new_title)


@dataclass(frozen=True)
class PlayerState:
    """
    Immutable snapshot of the playback state.
    FP Concept: Immutable State Container.
    """
    current_track: Optional[Track] = None
    is_playing: bool = False
    volume: float = 0.7  # Range 0.0 to 1.0
    position_sec: float = 0.0
    is_shuffled: bool = False