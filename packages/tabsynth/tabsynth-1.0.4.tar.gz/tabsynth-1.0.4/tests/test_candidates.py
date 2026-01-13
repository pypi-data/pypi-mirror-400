"""Tests for candidate generation."""

from tabsynth.model import NoteEvent, ChordEvent
from tabsynth.fretboard import build_fretboard, STANDARD_TUNING_HZ
from tabsynth.templates import V1_TEMPLATES
from tabsynth.candidates import (
    generate_note_candidates,
    generate_chord_candidates,
    generate_candidates,
    match_chord_template,
)


def test_generate_note_candidates():
    """Test generation of candidates for a single note."""
    fretboard = build_fretboard(STANDARD_TUNING_HZ)

    # A4 = 440 Hz
    note = NoteEvent(pitch_hz=440.0, start=0.0, duration=0.5)
    candidates = generate_note_candidates(note, fretboard, max_fret=15)

    # Should have multiple candidates (different string/fret positions)
    assert len(candidates) > 0

    # All candidates should be for notes
    for c in candidates:
        assert c.kind == "note"
        assert len(c.strings) == 1
        assert c.start == 0.0
        assert c.duration == 0.5

    # Check that at least one candidate uses string 1, fret 5 (A4)
    found_expected = False
    for c in candidates:
        if 1 in c.strings and c.frets_by_string.get(1) == 5:
            found_expected = True
            break
    assert found_expected, "Expected string 1, fret 5 for A4"


def test_generate_chord_candidates():
    """Test generation of candidates for a chord."""
    fretboard = build_fretboard(STANDARD_TUNING_HZ)

    # E major chord (E, G#, B)
    chord = ChordEvent(pitches_hz=[329.63, 415.30, 493.88], start=0.0, duration=1.0)
    candidates = generate_chord_candidates(chord, V1_TEMPLATES, fretboard)

    # Should have at least one candidate
    assert len(candidates) > 0

    # All candidates should be for chords
    for c in candidates:
        assert c.kind == "chord"
        assert len(c.strings) > 1
        assert c.start == 0.0
        assert c.duration == 1.0

    # Should find E major open chord
    found_e_major = False
    for c in candidates:
        if c.chord_id == "E_major_open":
            found_e_major = True
            break
    assert found_e_major, "Expected to find E major open chord"


def test_match_chord_template():
    """Test matching a chord to a specific template."""
    fretboard = build_fretboard(STANDARD_TUNING_HZ)

    # Find E major template
    e_major_template = None
    for t in V1_TEMPLATES:
        if t.id == "E_major_open":
            e_major_template = t
            break

    assert e_major_template is not None

    # E major chord
    chord = ChordEvent(pitches_hz=[329.63, 415.30, 493.88], start=0.0, duration=1.0)

    state = match_chord_template(chord, e_major_template, fretboard)

    # Should match
    assert state is not None
    assert state.chord_id == "E_major_open"
    assert state.kind == "chord"


def test_generate_candidates_note():
    """Test generate_candidates with a note event."""
    note = NoteEvent(pitch_hz=440.0, start=0.0, duration=0.5)
    candidates = generate_candidates(note)

    assert len(candidates) > 0
    for c in candidates:
        assert c.kind == "note"


def test_generate_candidates_chord():
    """Test generate_candidates with a chord event."""
    chord = ChordEvent(pitches_hz=[329.63, 415.30, 493.88], start=0.0, duration=1.0)
    candidates = generate_candidates(chord)

    assert len(candidates) > 0
    for c in candidates:
        assert c.kind == "chord"


def test_candidate_properties():
    """Test that candidates have correct properties."""
    fretboard = build_fretboard(STANDARD_TUNING_HZ)
    note = NoteEvent(pitch_hz=440.0, start=1.5, duration=0.25)
    candidates = generate_note_candidates(note, fretboard)

    for c in candidates:
        # Check time properties
        assert c.start == 1.5
        assert c.duration == 0.25

        # Check fret properties
        assert c.min_fret >= 0
        assert c.max_fret >= c.min_fret
        assert c.mean_fret >= c.min_fret
        assert c.mean_fret <= c.max_fret

        # For single notes, min/max/mean should be the same
        assert c.min_fret == c.max_fret
        assert c.mean_fret == c.min_fret
