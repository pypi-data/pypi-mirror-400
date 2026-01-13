"""Core data models for tabsynth."""

from dataclasses import dataclass
from typing import Literal

PlayableKind = Literal["note", "chord"]


@dataclass
class NoteEvent:
    """A single detected note."""

    pitch_hz: float
    start: float
    duration: float
    confidence: float = 1.0

    def __post_init__(self):
        if self.pitch_hz <= 0:
            raise ValueError("pitch_hz must be positive")
        if self.start < 0:
            raise ValueError("start must be non-negative")
        if self.duration <= 0:
            raise ValueError("duration must be positive")


@dataclass
class ChordEvent:
    """A detected chord (multiple pitches)."""

    pitches_hz: list[float]
    start: float
    duration: float
    confidence: float = 1.0

    def __post_init__(self):
        if not self.pitches_hz:
            raise ValueError("pitches_hz must not be empty")
        for p in self.pitches_hz:
            if p <= 0:
                raise ValueError("all pitches must be positive")
        if self.start < 0:
            raise ValueError("start must be non-negative")
        if self.duration <= 0:
            raise ValueError("duration must be positive")


Event = NoteEvent | ChordEvent


@dataclass
class PlayableState:
    """
    A playable guitar configuration (note or chord).
    Represents how to play notes on specific strings/frets.
    """

    start: float
    duration: float
    kind: PlayableKind
    strings: set[int]
    frets_by_string: dict[int, int]
    mean_fret: float
    min_fret: int
    max_fret: int
    requires_barre: bool = False
    chord_id: str | None = None

    def __post_init__(self):
        # Validate strings are in 1..6
        for s in self.strings:
            if s < 1 or s > 6:
                raise ValueError(f"string {s} must be in range 1..6")
        for s in self.frets_by_string:
            if s < 1 or s > 6:
                raise ValueError(f"string {s} must be in range 1..6")
