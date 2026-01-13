"""Chord templates for matching detected chords to playable guitar shapes."""

from dataclasses import dataclass


@dataclass
class ChordTemplate:
    """
    A chord template defining a playable guitar chord shape.

    Attributes:
        id: Unique identifier for the chord
        frets: List of 6 fret numbers (or None for muted strings), indexed by strings [6,5,4,3,2,1]
        barre: Whether this chord requires a barre technique
        pitch_classes: Set of pitch class names in the chord
        span: Fret span (max_fret - min_fret among fretted notes)
        tags: Set of descriptive tags (e.g., "open", "barre", "basic")
    """

    id: str
    frets: list[int | None]
    barre: bool
    pitch_classes: set[str]
    span: int
    tags: set[str]

    def __post_init__(self):
        if len(self.frets) != 6:
            raise ValueError(
                f"frets must have exactly 6 elements, got {len(self.frets)}"
            )


# V1 chord template library
V1_TEMPLATES: list[ChordTemplate] = [
    ChordTemplate(
        id="E_major_open",
        frets=[0, 2, 2, 1, 0, 0],
        barre=False,
        pitch_classes={"E", "G#", "B"},
        span=2,
        tags={"open", "basic"},
    ),
    ChordTemplate(
        id="E_minor_open",
        frets=[0, 2, 2, 0, 0, 0],
        barre=False,
        pitch_classes={"E", "G", "B"},
        span=2,
        tags={"open", "basic"},
    ),
    ChordTemplate(
        id="A_major_open",
        frets=[None, 0, 2, 2, 2, 0],
        barre=False,
        pitch_classes={"A", "C#", "E"},
        span=2,
        tags={"open", "basic"},
    ),
    ChordTemplate(
        id="A_minor_open",
        frets=[None, 0, 2, 2, 1, 0],
        barre=False,
        pitch_classes={"A", "C", "E"},
        span=2,
        tags={"open", "basic"},
    ),
    ChordTemplate(
        id="A_major_barre_Eshape",
        frets=[5, 7, 7, 6, 5, 5],
        barre=True,
        pitch_classes={"A", "C#", "E"},
        span=2,
        tags={"barre", "E-shape"},
    ),
]
