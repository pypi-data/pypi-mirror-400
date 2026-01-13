"""Tests for fretboard and pitch helpers."""

from tabsynth.fretboard import (
    build_fretboard,
    STANDARD_TUNING_HZ,
    cents_diff,
    hz_to_midi,
    hz_to_pitch_class,
    NOTE_NAMES,
)


def test_standard_tuning():
    """Test that standard tuning constants are defined correctly."""
    assert len(STANDARD_TUNING_HZ) == 6
    assert 6 in STANDARD_TUNING_HZ
    assert 1 in STANDARD_TUNING_HZ
    # E2 (low E)
    assert abs(STANDARD_TUNING_HZ[6] - 82.41) < 0.1
    # E4 (high E)
    assert abs(STANDARD_TUNING_HZ[1] - 329.63) < 0.1


def test_build_fretboard():
    """Test fretboard generation."""
    fretboard = build_fretboard(STANDARD_TUNING_HZ, max_fret=12)

    # Check structure
    assert len(fretboard) == 6
    for string in range(1, 7):
        assert string in fretboard
        assert len(fretboard[string]) == 13  # 0-12 frets

    # Check open string frequencies
    for string, open_hz in STANDARD_TUNING_HZ.items():
        assert abs(fretboard[string][0] - open_hz) < 0.01

    # Check 12th fret is one octave higher
    for string, open_hz in STANDARD_TUNING_HZ.items():
        fret_12 = fretboard[string][12]
        assert abs(fret_12 - open_hz * 2) < 0.1


def test_cents_diff():
    """Test cents difference calculation."""
    # Same frequency
    assert abs(cents_diff(440.0, 440.0)) < 0.01

    # One octave apart (1200 cents)
    assert abs(cents_diff(440.0, 880.0) - (-1200)) < 1
    assert abs(cents_diff(880.0, 440.0) - 1200) < 1

    # One semitone apart (100 cents)
    a4 = 440.0
    a_sharp = a4 * (2 ** (1 / 12))
    assert abs(abs(cents_diff(a4, a_sharp)) - 100) < 1


def test_hz_to_midi():
    """Test Hz to MIDI conversion."""
    # A4 = 440 Hz = MIDI 69
    assert abs(hz_to_midi(440.0) - 69.0) < 0.01

    # C4 = ~261.63 Hz = MIDI 60
    assert abs(hz_to_midi(261.63) - 60.0) < 0.1

    # A5 = 880 Hz = MIDI 81
    assert abs(hz_to_midi(880.0) - 81.0) < 0.01


def test_hz_to_pitch_class():
    """Test frequency to pitch class conversion."""
    # A4 = 440 Hz
    assert hz_to_pitch_class(440.0) == "A"

    # C4 = ~261.63 Hz
    assert hz_to_pitch_class(261.63) == "C"

    # E4 = ~329.63 Hz
    assert hz_to_pitch_class(329.63) == "E"

    # G#4 = ~415.30 Hz
    assert hz_to_pitch_class(415.30) in ["G#", "Ab"]  # Enharmonic


def test_note_names():
    """Test that NOTE_NAMES is complete."""
    assert len(NOTE_NAMES) == 12
    assert "C" in NOTE_NAMES
    assert "A" in NOTE_NAMES
    assert NOTE_NAMES[0] == "C"


def test_fretboard_accuracy():
    """Test that fretboard frequencies follow equal temperament."""
    fretboard = build_fretboard(STANDARD_TUNING_HZ, max_fret=24)

    # Check a few known values
    # String 6 (E2), fret 5 should be A2 (~110 Hz)
    assert abs(fretboard[6][5] - 110.0) < 0.5

    # String 5 (A2) is already 110 Hz at fret 0
    assert abs(fretboard[5][0] - 110.0) < 0.5

    # String 1 (E4), fret 5 should be A4 (440 Hz)
    assert abs(fretboard[1][5] - 440.0) < 1.0
