"""Tests for tabsynth data models."""

import pytest
from tabsynth.model import NoteEvent, ChordEvent, PlayableState


class TestNoteEvent:
    """Tests for NoteEvent dataclass."""

    def test_valid_note(self):
        """Test creating a valid NoteEvent."""
        note = NoteEvent(pitch_hz=440.0, start=0.0, duration=1.0)
        assert note.pitch_hz == 440.0
        assert note.start == 0.0
        assert note.duration == 1.0
        assert note.confidence == 1.0

    def test_with_confidence(self):
        """Test NoteEvent with custom confidence."""
        note = NoteEvent(pitch_hz=440.0, start=0.0, duration=1.0, confidence=0.8)
        assert note.confidence == 0.8

    def test_invalid_pitch_zero(self):
        """Test NoteEvent rejects zero pitch."""
        with pytest.raises(ValueError, match="pitch_hz must be positive"):
            NoteEvent(pitch_hz=0, start=0.0, duration=1.0)

    def test_invalid_pitch_negative(self):
        """Test NoteEvent rejects negative pitch."""
        with pytest.raises(ValueError, match="pitch_hz must be positive"):
            NoteEvent(pitch_hz=-440.0, start=0.0, duration=1.0)

    def test_invalid_start_negative(self):
        """Test NoteEvent rejects negative start."""
        with pytest.raises(ValueError, match="start must be non-negative"):
            NoteEvent(pitch_hz=440.0, start=-1.0, duration=1.0)

    def test_invalid_duration_zero(self):
        """Test NoteEvent rejects zero duration."""
        with pytest.raises(ValueError, match="duration must be positive"):
            NoteEvent(pitch_hz=440.0, start=0.0, duration=0)

    def test_invalid_duration_negative(self):
        """Test NoteEvent rejects negative duration."""
        with pytest.raises(ValueError, match="duration must be positive"):
            NoteEvent(pitch_hz=440.0, start=0.0, duration=-1.0)


class TestChordEvent:
    """Tests for ChordEvent dataclass."""

    def test_valid_chord(self):
        """Test creating a valid ChordEvent."""
        chord = ChordEvent(pitches_hz=[440.0, 550.0], start=0.0, duration=1.0)
        assert chord.pitches_hz == [440.0, 550.0]
        assert chord.start == 0.0
        assert chord.duration == 1.0

    def test_empty_pitches(self):
        """Test ChordEvent rejects empty pitches."""
        with pytest.raises(ValueError, match="pitches_hz must not be empty"):
            ChordEvent(pitches_hz=[], start=0.0, duration=1.0)

    def test_invalid_pitch_in_chord(self):
        """Test ChordEvent rejects non-positive pitch."""
        with pytest.raises(ValueError, match="all pitches must be positive"):
            ChordEvent(pitches_hz=[440.0, -220.0], start=0.0, duration=1.0)

    def test_zero_pitch_in_chord(self):
        """Test ChordEvent rejects zero pitch."""
        with pytest.raises(ValueError, match="all pitches must be positive"):
            ChordEvent(pitches_hz=[440.0, 0], start=0.0, duration=1.0)

    def test_invalid_start_negative(self):
        """Test ChordEvent rejects negative start."""
        with pytest.raises(ValueError, match="start must be non-negative"):
            ChordEvent(pitches_hz=[440.0], start=-1.0, duration=1.0)

    def test_invalid_duration_zero(self):
        """Test ChordEvent rejects zero duration."""
        with pytest.raises(ValueError, match="duration must be positive"):
            ChordEvent(pitches_hz=[440.0], start=0.0, duration=0)

    def test_invalid_duration_negative(self):
        """Test ChordEvent rejects negative duration."""
        with pytest.raises(ValueError, match="duration must be positive"):
            ChordEvent(pitches_hz=[440.0], start=0.0, duration=-1.0)


class TestPlayableState:
    """Tests for PlayableState dataclass."""

    def test_valid_note_state(self):
        """Test creating a valid PlayableState for a note."""
        state = PlayableState(
            start=0.0,
            duration=1.0,
            kind="note",
            strings={1},
            frets_by_string={1: 5},
            mean_fret=5.0,
            min_fret=5,
            max_fret=5,
        )
        assert state.kind == "note"
        assert state.strings == {1}

    def test_valid_chord_state(self):
        """Test creating a valid PlayableState for a chord."""
        state = PlayableState(
            start=0.0,
            duration=1.0,
            kind="chord",
            strings={1, 2, 3},
            frets_by_string={1: 0, 2: 2, 3: 2},
            mean_fret=1.33,
            min_fret=0,
            max_fret=2,
            requires_barre=False,
            chord_id="Am",
        )
        assert state.kind == "chord"
        assert state.chord_id == "Am"

    def test_invalid_string_zero(self):
        """Test PlayableState rejects string 0."""
        with pytest.raises(ValueError, match="string 0 must be in range 1..6"):
            PlayableState(
                start=0.0,
                duration=1.0,
                kind="note",
                strings={0},
                frets_by_string={0: 5},
                mean_fret=5.0,
                min_fret=5,
                max_fret=5,
            )

    def test_invalid_string_seven(self):
        """Test PlayableState rejects string 7."""
        with pytest.raises(ValueError, match="string 7 must be in range 1..6"):
            PlayableState(
                start=0.0,
                duration=1.0,
                kind="note",
                strings={7},
                frets_by_string={7: 5},
                mean_fret=5.0,
                min_fret=5,
                max_fret=5,
            )

    def test_invalid_string_in_frets_dict(self):
        """Test PlayableState rejects invalid string in frets_by_string."""
        with pytest.raises(ValueError, match="string 0 must be in range 1..6"):
            PlayableState(
                start=0.0,
                duration=1.0,
                kind="note",
                strings={1},
                frets_by_string={0: 5},  # Invalid string in dict
                mean_fret=5.0,
                min_fret=5,
                max_fret=5,
            )
