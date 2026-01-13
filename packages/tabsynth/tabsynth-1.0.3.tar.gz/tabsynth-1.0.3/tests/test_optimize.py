"""Tests for optimization."""

from tabsynth.model import NoteEvent, ChordEvent
from tabsynth.optimize import optimize_sequence, optimize_single_event
from tabsynth.templates import V1_TEMPLATES


def test_optimize_single_event_note():
    """Test optimization of a single note event."""
    note = NoteEvent(pitch_hz=440.0, start=0.0, duration=0.5)
    result = optimize_single_event(note)

    assert result is not None
    assert result.kind == "note"
    assert result.start == 0.0
    assert result.duration == 0.5


def test_optimize_single_event_chord():
    """Test optimization of a single chord event."""
    chord = ChordEvent(pitches_hz=[329.63, 415.30, 493.88], start=0.0, duration=1.0)
    result = optimize_single_event(chord)

    assert result is not None
    assert result.kind == "chord"


def test_optimize_sequence_notes():
    """Test optimization of a sequence of notes."""
    events = [
        NoteEvent(pitch_hz=329.63, start=0.0, duration=0.5),
        NoteEvent(pitch_hz=369.99, start=0.5, duration=0.5),
        NoteEvent(pitch_hz=392.00, start=1.0, duration=0.5),
        NoteEvent(pitch_hz=440.00, start=1.5, duration=0.5),
    ]

    result = optimize_sequence(events)

    # Should return same number of states as events
    assert len(result) == len(events)

    # All should be notes
    for state in result:
        assert state.kind == "note"

    # Check temporal ordering is preserved
    for i in range(len(result)):
        assert result[i].start == events[i].start


def test_optimize_sequence_chords():
    """Test optimization of a sequence of chords."""
    events = [
        ChordEvent(pitches_hz=[329.63, 415.30, 493.88], start=0.0, duration=1.0),
        ChordEvent(pitches_hz=[440.00, 554.37, 659.26], start=1.0, duration=1.0),
    ]

    result = optimize_sequence(events, templates=V1_TEMPLATES)

    # Should have states for chords
    assert len(result) > 0

    # All should be chords
    for state in result:
        assert state.kind == "chord"


def test_optimize_sequence_mixed():
    """Test optimization of mixed notes and chords."""
    events = [
        ChordEvent(pitches_hz=[329.63, 415.30, 493.88], start=0.0, duration=1.0),
        NoteEvent(pitch_hz=440.0, start=1.0, duration=0.5),
        NoteEvent(pitch_hz=493.88, start=1.5, duration=0.5),
    ]

    result = optimize_sequence(events)

    assert len(result) == 3
    assert result[0].kind == "chord"
    assert result[1].kind == "note"
    assert result[2].kind == "note"


def test_optimize_empty_sequence():
    """Test optimization of an empty sequence."""
    result = optimize_sequence([])
    assert result == []


def test_optimize_preserves_timing():
    """Test that optimization preserves event timing."""
    events = [
        NoteEvent(pitch_hz=440.0, start=0.0, duration=0.5),
        NoteEvent(pitch_hz=493.88, start=0.5, duration=0.5),
        NoteEvent(pitch_hz=523.25, start=1.0, duration=1.0),
    ]

    result = optimize_sequence(events)

    for i, state in enumerate(result):
        assert state.start == events[i].start
        assert state.duration == events[i].duration


def test_optimize_prefers_efficient_transitions():
    """Test that optimization minimizes transition costs."""
    # Create a sequence of notes on the same string
    # to encourage staying in the same position
    events = [
        NoteEvent(pitch_hz=440.0, start=0.0, duration=0.5),  # A4
        NoteEvent(pitch_hz=493.88, start=0.5, duration=0.5),  # B4
        NoteEvent(pitch_hz=523.25, start=1.0, duration=0.5),  # C5
    ]

    result = optimize_sequence(events)

    # Should return valid states
    assert len(result) == 3

    # Check that positions are reasonably close (not jumping all over)
    fret_positions = [state.mean_fret for state in result]
    max_jump = max(
        abs(fret_positions[i + 1] - fret_positions[i])
        for i in range(len(fret_positions) - 1)
    )

    # With optimization, shouldn't have huge jumps for this simple sequence
    assert max_jump < 12, "Optimization should avoid large position jumps"
