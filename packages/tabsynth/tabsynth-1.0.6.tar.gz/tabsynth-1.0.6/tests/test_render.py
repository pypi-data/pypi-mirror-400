"""Tests for tablature rendering functions."""

import json
from tabsynth.model import PlayableState
from tabsynth.render import (
    render_ascii,
    render_json,
    render_compact,
    format_tablature_section,
)


def _make_note_state(string: int, fret: int, start: float = 0.0) -> PlayableState:
    """Helper to create a simple note state."""
    return PlayableState(
        start=start,
        duration=0.5,
        kind="note",
        strings={string},
        frets_by_string={string: fret},
        mean_fret=float(fret),
        min_fret=fret,
        max_fret=fret,
    )


def _make_chord_state(
    frets: dict[int, int], chord_id: str = None, start: float = 0.0
) -> PlayableState:
    """Helper to create a chord state."""
    strings = set(frets.keys())
    fret_vals = list(frets.values())
    return PlayableState(
        start=start,
        duration=0.5,
        kind="chord",
        strings=strings,
        frets_by_string=frets,
        mean_fret=sum(fret_vals) / len(fret_vals),
        min_fret=min(fret_vals),
        max_fret=max(fret_vals),
        chord_id=chord_id,
    )


class TestRenderAscii:
    """Tests for render_ascii function."""

    def test_empty_states(self):
        """Test render_ascii with empty list."""
        result = render_ascii([])
        assert result == ""

    def test_single_note(self):
        """Test render_ascii with single note."""
        states = [_make_note_state(string=1, fret=5)]
        result = render_ascii(states)
        assert "Guitar Tablature" in result
        assert "e|5|" in result

    def test_multiple_notes(self):
        """Test render_ascii with multiple notes."""
        states = [
            _make_note_state(string=1, fret=5, start=0.0),
            _make_note_state(string=2, fret=3, start=0.5),
        ]
        result = render_ascii(states)
        assert "e|5--" in result
        assert "B|--3" in result

    def test_chord_legend(self):
        """Test render_ascii shows chord legend."""
        states = [
            _make_chord_state({1: 0, 2: 0, 3: 1, 4: 2, 5: 2, 6: 0}, chord_id="E_major")
        ]
        result = render_ascii(states)
        assert "Chords:" in result
        assert "E_major" in result

    def test_no_chord_legend_when_no_chords(self):
        """Test render_ascii doesn't show legend when no chord_ids."""
        states = [_make_note_state(string=1, fret=5)]
        result = render_ascii(states)
        assert "Chords:" not in result

    def test_chord_legend_dedupes(self):
        """Test render_ascii deduplicates chord IDs in legend."""
        states = [
            _make_chord_state({1: 0, 2: 0}, chord_id="Am"),
            _make_chord_state({1: 0, 2: 0}, chord_id="Am"),  # Same chord twice
            _make_chord_state({1: 2, 2: 2}, chord_id="Bm"),
        ]
        result = render_ascii(states)
        # Should only list each chord once
        assert result.count("Am") == 1
        assert result.count("Bm") == 1


class TestRenderJson:
    """Tests for render_json function."""

    def test_empty_states(self):
        """Test render_json with empty list."""
        result = render_json([])
        assert json.loads(result) == []

    def test_single_note(self):
        """Test render_json with single note."""
        states = [_make_note_state(string=3, fret=7)]
        result = render_json(states)
        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["index"] == 0
        assert data[0]["kind"] == "note"
        assert "3" in data[0]["frets"]
        assert data[0]["frets"]["3"] == 7


class TestRenderCompact:
    """Tests for render_compact function."""

    def test_empty_states(self):
        """Test render_compact with empty list."""
        result = render_compact([])
        assert result == "No states"

    def test_single_note(self):
        """Test render_compact with single note."""
        states = [_make_note_state(string=1, fret=5)]
        result = render_compact(states)
        assert "0: t=0.00 note [1:5]" in result

    def test_chord_with_id(self):
        """Test render_compact shows chord ID."""
        states = [_make_chord_state({1: 0, 2: 1, 3: 0}, chord_id="Am")]
        result = render_compact(states)
        assert "Am [" in result
        assert "1:0" in result

    def test_chord_without_id(self):
        """Test render_compact shows 'note' for chord without ID."""
        states = [_make_chord_state({1: 0, 2: 1, 3: 0}, chord_id=None)]
        result = render_compact(states)
        assert "note [" in result


class TestFormatTablatureSection:
    """Tests for format_tablature_section function."""

    def test_basic_format(self):
        """Test format_tablature_section returns ascii tab."""
        states = [_make_note_state(string=1, fret=5)]
        result = format_tablature_section(states)
        # Currently just calls render_ascii
        assert "Guitar Tablature" in result
        assert "e|5|" in result

    def test_empty_states(self):
        """Test format_tablature_section with empty list."""
        result = format_tablature_section([])
        assert result == ""
