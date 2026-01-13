"""Candidate generation for converting events to playable states."""

from typing import Optional
from tabsynth.model import Event, NoteEvent, ChordEvent, PlayableState
from tabsynth.fretboard import (
    build_fretboard,
    STANDARD_TUNING_HZ,
    cents_diff,
    hz_to_pitch_class,
)
from tabsynth.templates import ChordTemplate, V1_TEMPLATES


def generate_note_candidates(
    note: NoteEvent,
    fretboard: dict[int, dict[int, float]],
    max_fret: int = 15,
    tolerance_cents: float = 50.0,
) -> list[PlayableState]:
    """
    Generate candidate playable states for a single note.

    Args:
        note: The note event to convert
        fretboard: Fretboard mapping from build_fretboard
        max_fret: Maximum fret to consider
        tolerance_cents: Maximum pitch difference in cents to consider a match

    Returns:
        List of candidate PlayableState objects
    """
    candidates = []

    for string in range(1, 7):  # Strings 1-6
        for fret in range(max_fret + 1):
            fret_pitch = fretboard[string][fret]
            diff = abs(cents_diff(note.pitch_hz, fret_pitch))

            if diff <= tolerance_cents:
                state = PlayableState(
                    start=note.start,
                    duration=note.duration,
                    kind="note",
                    strings={string},
                    frets_by_string={string: fret},
                    mean_fret=float(fret),
                    min_fret=fret,
                    max_fret=fret,
                    requires_barre=False,
                    chord_id=None,
                )
                candidates.append(state)

    return candidates


def match_chord_template(
    chord: ChordEvent,
    template: ChordTemplate,
    fretboard: dict[int, dict[int, float]],
    tolerance_cents: float = 50.0,
) -> Optional[PlayableState]:
    """
    Try to match a chord event to a specific template.

    Args:
        chord: The chord event to match
        template: The template to match against
        fretboard: Fretboard mapping
        tolerance_cents: Pitch matching tolerance

    Returns:
        PlayableState if template matches, None otherwise
    """
    # Extract pitch classes from detected chord
    detected_classes = {hz_to_pitch_class(hz) for hz in chord.pitches_hz}

    # Check if detected pitch classes match template pitch classes
    # Allow subset matching (template may have more notes)
    if not detected_classes.issubset(
        template.pitch_classes
    ) and not template.pitch_classes.issubset(detected_classes):
        # Check for significant overlap
        overlap = detected_classes & template.pitch_classes
        if len(overlap) < min(2, len(detected_classes)):
            return None

    # Build PlayableState from template
    strings = set()
    frets_by_string = {}
    fret_values = []

    for string_idx, fret in enumerate(template.frets):
        string = 6 - string_idx  # Convert index to string number (6,5,4,3,2,1)
        if fret is not None:
            strings.add(string)
            frets_by_string[string] = fret
            fret_values.append(fret)

    if not fret_values:
        return None

    mean_fret = sum(fret_values) / len(fret_values)
    min_fret = min(fret_values)
    max_fret = max(fret_values)

    return PlayableState(
        start=chord.start,
        duration=chord.duration,
        kind="chord",
        strings=strings,
        frets_by_string=frets_by_string,
        mean_fret=mean_fret,
        min_fret=min_fret,
        max_fret=max_fret,
        requires_barre=template.barre,
        chord_id=template.id,
    )


def generate_chord_candidates(
    chord: ChordEvent,
    templates: list[ChordTemplate] = None,
    fretboard: dict[int, dict[int, float]] = None,
    tolerance_cents: float = 50.0,
) -> list[PlayableState]:
    """
    Generate candidate playable states for a chord by matching templates.

    Args:
        chord: The chord event to convert
        templates: List of chord templates to match (default: V1_TEMPLATES)
        fretboard: Fretboard mapping (default: standard tuning)
        tolerance_cents: Pitch matching tolerance

    Returns:
        List of candidate PlayableState objects
    """
    if templates is None:
        templates = V1_TEMPLATES
    if fretboard is None:
        fretboard = build_fretboard(STANDARD_TUNING_HZ)

    candidates = []

    for template in templates:
        state = match_chord_template(chord, template, fretboard, tolerance_cents)
        if state is not None:
            candidates.append(state)

    return candidates


def generate_candidates(
    event: Event,
    templates: list[ChordTemplate] = None,
    fretboard: dict[int, dict[int, float]] = None,
    max_fret: int = 15,
    tolerance_cents: float = 50.0,
) -> list[PlayableState]:
    """
    Generate all candidate playable states for an event (note or chord).

    Args:
        event: The event to convert
        templates: Chord templates for chord matching
        fretboard: Fretboard mapping
        max_fret: Maximum fret for note candidates
        tolerance_cents: Pitch matching tolerance

    Returns:
        List of candidate PlayableState objects
    """
    if fretboard is None:
        fretboard = build_fretboard(STANDARD_TUNING_HZ)

    if isinstance(event, NoteEvent):
        return generate_note_candidates(event, fretboard, max_fret, tolerance_cents)
    elif isinstance(event, ChordEvent):
        return generate_chord_candidates(event, templates, fretboard, tolerance_cents)
    else:
        return []
