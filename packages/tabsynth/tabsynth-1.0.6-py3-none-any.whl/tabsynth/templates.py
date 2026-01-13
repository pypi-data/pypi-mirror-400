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
    # ==========================================================================
    # OPEN MAJOR CHORDS
    # ==========================================================================
    ChordTemplate(
        id="E_major_open",
        frets=[0, 2, 2, 1, 0, 0],
        barre=False,
        pitch_classes={"E", "G#", "B"},
        span=2,
        tags={"open", "basic", "major"},
    ),
    ChordTemplate(
        id="A_major_open",
        frets=[None, 0, 2, 2, 2, 0],
        barre=False,
        pitch_classes={"A", "C#", "E"},
        span=2,
        tags={"open", "basic", "major"},
    ),
    ChordTemplate(
        id="D_major_open",
        frets=[None, None, 0, 2, 3, 2],
        barre=False,
        pitch_classes={"D", "F#", "A"},
        span=3,
        tags={"open", "basic", "major"},
    ),
    ChordTemplate(
        id="G_major_open",
        frets=[3, 2, 0, 0, 0, 3],
        barre=False,
        pitch_classes={"G", "B", "D"},
        span=3,
        tags={"open", "basic", "major"},
    ),
    ChordTemplate(
        id="G_major_open_alt",
        frets=[3, 2, 0, 0, 3, 3],
        barre=False,
        pitch_classes={"G", "B", "D"},
        span=3,
        tags={"open", "major"},
    ),
    ChordTemplate(
        id="C_major_open",
        frets=[None, 3, 2, 0, 1, 0],
        barre=False,
        pitch_classes={"C", "E", "G"},
        span=3,
        tags={"open", "basic", "major"},
    ),
    # ==========================================================================
    # OPEN MINOR CHORDS
    # ==========================================================================
    ChordTemplate(
        id="E_minor_open",
        frets=[0, 2, 2, 0, 0, 0],
        barre=False,
        pitch_classes={"E", "G", "B"},
        span=2,
        tags={"open", "basic", "minor"},
    ),
    ChordTemplate(
        id="A_minor_open",
        frets=[None, 0, 2, 2, 1, 0],
        barre=False,
        pitch_classes={"A", "C", "E"},
        span=2,
        tags={"open", "basic", "minor"},
    ),
    ChordTemplate(
        id="D_minor_open",
        frets=[None, None, 0, 2, 3, 1],
        barre=False,
        pitch_classes={"D", "F", "A"},
        span=3,
        tags={"open", "basic", "minor"},
    ),
    # ==========================================================================
    # SEVENTH CHORDS (DOMINANT 7)
    # ==========================================================================
    ChordTemplate(
        id="E7_open",
        frets=[0, 2, 0, 1, 0, 0],
        barre=False,
        pitch_classes={"E", "G#", "B", "D"},
        span=2,
        tags={"open", "seventh", "dominant"},
    ),
    ChordTemplate(
        id="A7_open",
        frets=[None, 0, 2, 0, 2, 0],
        barre=False,
        pitch_classes={"A", "C#", "E", "G"},
        span=2,
        tags={"open", "seventh", "dominant"},
    ),
    ChordTemplate(
        id="D7_open",
        frets=[None, None, 0, 2, 1, 2],
        barre=False,
        pitch_classes={"D", "F#", "A", "C"},
        span=2,
        tags={"open", "seventh", "dominant"},
    ),
    ChordTemplate(
        id="G7_open",
        frets=[3, 2, 0, 0, 0, 1],
        barre=False,
        pitch_classes={"G", "B", "D", "F"},
        span=3,
        tags={"open", "seventh", "dominant"},
    ),
    ChordTemplate(
        id="C7_open",
        frets=[None, 3, 2, 3, 1, 0],
        barre=False,
        pitch_classes={"C", "E", "G", "Bb"},
        span=3,
        tags={"open", "seventh", "dominant"},
    ),
    ChordTemplate(
        id="B7_open",
        frets=[None, 2, 1, 2, 0, 2],
        barre=False,
        pitch_classes={"B", "D#", "F#", "A"},
        span=2,
        tags={"open", "seventh", "dominant"},
    ),
    # ==========================================================================
    # MAJOR SEVENTH CHORDS
    # ==========================================================================
    ChordTemplate(
        id="Cmaj7_open",
        frets=[None, 3, 2, 0, 0, 0],
        barre=False,
        pitch_classes={"C", "E", "G", "B"},
        span=3,
        tags={"open", "seventh", "major7"},
    ),
    ChordTemplate(
        id="Dmaj7_open",
        frets=[None, None, 0, 2, 2, 2],
        barre=False,
        pitch_classes={"D", "F#", "A", "C#"},
        span=2,
        tags={"open", "seventh", "major7"},
    ),
    ChordTemplate(
        id="Gmaj7_open",
        frets=[3, 2, 0, 0, 0, 2],
        barre=False,
        pitch_classes={"G", "B", "D", "F#"},
        span=3,
        tags={"open", "seventh", "major7"},
    ),
    ChordTemplate(
        id="Amaj7_open",
        frets=[None, 0, 2, 1, 2, 0],
        barre=False,
        pitch_classes={"A", "C#", "E", "G#"},
        span=2,
        tags={"open", "seventh", "major7"},
    ),
    ChordTemplate(
        id="Emaj7_open",
        frets=[0, 2, 1, 1, 0, 0],
        barre=False,
        pitch_classes={"E", "G#", "B", "D#"},
        span=2,
        tags={"open", "seventh", "major7"},
    ),
    # ==========================================================================
    # MINOR SEVENTH CHORDS
    # ==========================================================================
    ChordTemplate(
        id="Em7_open",
        frets=[0, 2, 0, 0, 0, 0],
        barre=False,
        pitch_classes={"E", "G", "B", "D"},
        span=2,
        tags={"open", "seventh", "minor7"},
    ),
    ChordTemplate(
        id="Am7_open",
        frets=[None, 0, 2, 0, 1, 0],
        barre=False,
        pitch_classes={"A", "C", "E", "G"},
        span=2,
        tags={"open", "seventh", "minor7"},
    ),
    ChordTemplate(
        id="Dm7_open",
        frets=[None, None, 0, 2, 1, 1],
        barre=False,
        pitch_classes={"D", "F", "A", "C"},
        span=2,
        tags={"open", "seventh", "minor7"},
    ),
    # ==========================================================================
    # SUSPENDED CHORDS
    # ==========================================================================
    ChordTemplate(
        id="Dsus2_open",
        frets=[None, None, 0, 2, 3, 0],
        barre=False,
        pitch_classes={"D", "E", "A"},
        span=3,
        tags={"open", "suspended", "sus2"},
    ),
    ChordTemplate(
        id="Dsus4_open",
        frets=[None, None, 0, 2, 3, 3],
        barre=False,
        pitch_classes={"D", "G", "A"},
        span=3,
        tags={"open", "suspended", "sus4"},
    ),
    ChordTemplate(
        id="Asus2_open",
        frets=[None, 0, 2, 2, 0, 0],
        barre=False,
        pitch_classes={"A", "B", "E"},
        span=2,
        tags={"open", "suspended", "sus2"},
    ),
    ChordTemplate(
        id="Asus4_open",
        frets=[None, 0, 2, 2, 3, 0],
        barre=False,
        pitch_classes={"A", "D", "E"},
        span=3,
        tags={"open", "suspended", "sus4"},
    ),
    ChordTemplate(
        id="Esus4_open",
        frets=[0, 2, 2, 2, 0, 0],
        barre=False,
        pitch_classes={"E", "A", "B"},
        span=2,
        tags={"open", "suspended", "sus4"},
    ),
    # ==========================================================================
    # ADD9 CHORDS
    # ==========================================================================
    ChordTemplate(
        id="Cadd9_open",
        frets=[None, 3, 2, 0, 3, 0],
        barre=False,
        pitch_classes={"C", "E", "G", "D"},
        span=3,
        tags={"open", "add9"},
    ),
    ChordTemplate(
        id="Gadd9_open",
        frets=[3, 2, 0, 2, 0, 3],
        barre=False,
        pitch_classes={"G", "B", "D", "A"},
        span=3,
        tags={"open", "add9"},
    ),
    # ==========================================================================
    # BARRE CHORDS - E MAJOR SHAPE
    # ==========================================================================
    ChordTemplate(
        id="F_major_barre_Eshape",
        frets=[1, 3, 3, 2, 1, 1],
        barre=True,
        pitch_classes={"F", "A", "C"},
        span=2,
        tags={"barre", "E-shape", "major"},
    ),
    ChordTemplate(
        id="F#_major_barre_Eshape",
        frets=[2, 4, 4, 3, 2, 2],
        barre=True,
        pitch_classes={"F#", "A#", "C#"},
        span=2,
        tags={"barre", "E-shape", "major"},
    ),
    ChordTemplate(
        id="G_major_barre_Eshape",
        frets=[3, 5, 5, 4, 3, 3],
        barre=True,
        pitch_classes={"G", "B", "D"},
        span=2,
        tags={"barre", "E-shape", "major"},
    ),
    ChordTemplate(
        id="Ab_major_barre_Eshape",
        frets=[4, 6, 6, 5, 4, 4],
        barre=True,
        pitch_classes={"Ab", "C", "Eb"},
        span=2,
        tags={"barre", "E-shape", "major"},
    ),
    ChordTemplate(
        id="A_major_barre_Eshape",
        frets=[5, 7, 7, 6, 5, 5],
        barre=True,
        pitch_classes={"A", "C#", "E"},
        span=2,
        tags={"barre", "E-shape", "major"},
    ),
    ChordTemplate(
        id="Bb_major_barre_Eshape",
        frets=[6, 8, 8, 7, 6, 6],
        barre=True,
        pitch_classes={"Bb", "D", "F"},
        span=2,
        tags={"barre", "E-shape", "major"},
    ),
    ChordTemplate(
        id="B_major_barre_Eshape",
        frets=[7, 9, 9, 8, 7, 7],
        barre=True,
        pitch_classes={"B", "D#", "F#"},
        span=2,
        tags={"barre", "E-shape", "major"},
    ),
    ChordTemplate(
        id="C_major_barre_Eshape",
        frets=[8, 10, 10, 9, 8, 8],
        barre=True,
        pitch_classes={"C", "E", "G"},
        span=2,
        tags={"barre", "E-shape", "major"},
    ),
    # ==========================================================================
    # BARRE CHORDS - E MINOR SHAPE
    # ==========================================================================
    ChordTemplate(
        id="F_minor_barre_Eshape",
        frets=[1, 3, 3, 1, 1, 1],
        barre=True,
        pitch_classes={"F", "Ab", "C"},
        span=2,
        tags={"barre", "E-shape", "minor"},
    ),
    ChordTemplate(
        id="F#_minor_barre_Eshape",
        frets=[2, 4, 4, 2, 2, 2],
        barre=True,
        pitch_classes={"F#", "A", "C#"},
        span=2,
        tags={"barre", "E-shape", "minor"},
    ),
    ChordTemplate(
        id="G_minor_barre_Eshape",
        frets=[3, 5, 5, 3, 3, 3],
        barre=True,
        pitch_classes={"G", "Bb", "D"},
        span=2,
        tags={"barre", "E-shape", "minor"},
    ),
    ChordTemplate(
        id="G#_minor_barre_Eshape",
        frets=[4, 6, 6, 4, 4, 4],
        barre=True,
        pitch_classes={"G#", "B", "D#"},
        span=2,
        tags={"barre", "E-shape", "minor"},
    ),
    ChordTemplate(
        id="A_minor_barre_Eshape",
        frets=[5, 7, 7, 5, 5, 5],
        barre=True,
        pitch_classes={"A", "C", "E"},
        span=2,
        tags={"barre", "E-shape", "minor"},
    ),
    ChordTemplate(
        id="Bb_minor_barre_Eshape",
        frets=[6, 8, 8, 6, 6, 6],
        barre=True,
        pitch_classes={"Bb", "Db", "F"},
        span=2,
        tags={"barre", "E-shape", "minor"},
    ),
    ChordTemplate(
        id="B_minor_barre_Eshape",
        frets=[7, 9, 9, 7, 7, 7],
        barre=True,
        pitch_classes={"B", "D", "F#"},
        span=2,
        tags={"barre", "E-shape", "minor"},
    ),
    # ==========================================================================
    # BARRE CHORDS - A MAJOR SHAPE
    # ==========================================================================
    ChordTemplate(
        id="Bb_major_barre_Ashape",
        frets=[None, 1, 3, 3, 3, 1],
        barre=True,
        pitch_classes={"Bb", "D", "F"},
        span=2,
        tags={"barre", "A-shape", "major"},
    ),
    ChordTemplate(
        id="B_major_barre_Ashape",
        frets=[None, 2, 4, 4, 4, 2],
        barre=True,
        pitch_classes={"B", "D#", "F#"},
        span=2,
        tags={"barre", "A-shape", "major"},
    ),
    ChordTemplate(
        id="C_major_barre_Ashape",
        frets=[None, 3, 5, 5, 5, 3],
        barre=True,
        pitch_classes={"C", "E", "G"},
        span=2,
        tags={"barre", "A-shape", "major"},
    ),
    ChordTemplate(
        id="C#_major_barre_Ashape",
        frets=[None, 4, 6, 6, 6, 4],
        barre=True,
        pitch_classes={"C#", "E#", "G#"},
        span=2,
        tags={"barre", "A-shape", "major"},
    ),
    ChordTemplate(
        id="D_major_barre_Ashape",
        frets=[None, 5, 7, 7, 7, 5],
        barre=True,
        pitch_classes={"D", "F#", "A"},
        span=2,
        tags={"barre", "A-shape", "major"},
    ),
    ChordTemplate(
        id="Eb_major_barre_Ashape",
        frets=[None, 6, 8, 8, 8, 6],
        barre=True,
        pitch_classes={"Eb", "G", "Bb"},
        span=2,
        tags={"barre", "A-shape", "major"},
    ),
    # ==========================================================================
    # BARRE CHORDS - A MINOR SHAPE
    # ==========================================================================
    ChordTemplate(
        id="Bb_minor_barre_Ashape",
        frets=[None, 1, 3, 3, 2, 1],
        barre=True,
        pitch_classes={"Bb", "Db", "F"},
        span=2,
        tags={"barre", "A-shape", "minor"},
    ),
    ChordTemplate(
        id="B_minor_barre_Ashape",
        frets=[None, 2, 4, 4, 3, 2],
        barre=True,
        pitch_classes={"B", "D", "F#"},
        span=2,
        tags={"barre", "A-shape", "minor"},
    ),
    ChordTemplate(
        id="C_minor_barre_Ashape",
        frets=[None, 3, 5, 5, 4, 3],
        barre=True,
        pitch_classes={"C", "Eb", "G"},
        span=2,
        tags={"barre", "A-shape", "minor"},
    ),
    ChordTemplate(
        id="C#_minor_barre_Ashape",
        frets=[None, 4, 6, 6, 5, 4],
        barre=True,
        pitch_classes={"C#", "E", "G#"},
        span=2,
        tags={"barre", "A-shape", "minor"},
    ),
    ChordTemplate(
        id="D_minor_barre_Ashape",
        frets=[None, 5, 7, 7, 6, 5],
        barre=True,
        pitch_classes={"D", "F", "A"},
        span=2,
        tags={"barre", "A-shape", "minor"},
    ),
    # ==========================================================================
    # POWER CHORDS (5TH CHORDS)
    # ==========================================================================
    ChordTemplate(
        id="E5_power",
        frets=[0, 2, 2, None, None, None],
        barre=False,
        pitch_classes={"E", "B"},
        span=2,
        tags={"power", "5th"},
    ),
    ChordTemplate(
        id="A5_power",
        frets=[None, 0, 2, 2, None, None],
        barre=False,
        pitch_classes={"A", "E"},
        span=2,
        tags={"power", "5th"},
    ),
    ChordTemplate(
        id="D5_power",
        frets=[None, None, 0, 2, 3, None],
        barre=False,
        pitch_classes={"D", "A"},
        span=3,
        tags={"power", "5th"},
    ),
    ChordTemplate(
        id="G5_power",
        frets=[3, 5, 5, None, None, None],
        barre=False,
        pitch_classes={"G", "D"},
        span=2,
        tags={"power", "5th"},
    ),
    ChordTemplate(
        id="F5_power",
        frets=[1, 3, 3, None, None, None],
        barre=True,
        pitch_classes={"F", "C"},
        span=2,
        tags={"power", "5th", "barre"},
    ),
    ChordTemplate(
        id="C5_power",
        frets=[None, 3, 5, 5, None, None],
        barre=False,
        pitch_classes={"C", "G"},
        span=2,
        tags={"power", "5th"},
    ),
    ChordTemplate(
        id="B5_power",
        frets=[None, 2, 4, 4, None, None],
        barre=False,
        pitch_classes={"B", "F#"},
        span=2,
        tags={"power", "5th"},
    ),
]
