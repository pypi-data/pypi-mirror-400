"""Tests for CLI module."""

import sys
from unittest.mock import patch
from io import StringIO

from tabsynth.cli import main, demo_notes, demo_chords, demo_mixed


class TestDemoFunctions:
    """Tests for demo data generation functions."""

    def test_demo_notes_returns_note_events(self):
        """demo_notes returns list of NoteEvents."""
        events = demo_notes()
        assert len(events) == 4
        for event in events:
            assert hasattr(event, "pitch_hz")
            assert hasattr(event, "start")
            assert hasattr(event, "duration")

    def test_demo_chords_returns_chord_events(self):
        """demo_chords returns list of ChordEvents."""
        events = demo_chords()
        assert len(events) == 3
        for event in events:
            assert hasattr(event, "pitches_hz")
            assert hasattr(event, "start")
            assert hasattr(event, "duration")

    def test_demo_mixed_returns_mixed_events(self):
        """demo_mixed returns list of mixed NoteEvents and ChordEvents."""
        events = demo_mixed()
        assert len(events) == 4
        # Check we have both types
        has_note = any(hasattr(e, "pitch_hz") for e in events)
        has_chord = any(hasattr(e, "pitches_hz") for e in events)
        assert has_note
        assert has_chord


class TestMainCLI:
    """Tests for main CLI entry point."""

    def test_help_no_args(self):
        """Running with no args shows help."""
        with patch.object(sys, "argv", ["tabsynth"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "tabsynth" in output
                assert "demo-notes" in output

    def test_help_command(self):
        """Running with 'help' shows help."""
        with patch.object(sys, "argv", ["tabsynth", "help"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "Usage:" in output

    def test_demo_notes_command(self):
        """Running demo-notes generates tablature."""
        with patch.object(sys, "argv", ["tabsynth", "demo-notes"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "Demo: Single Notes" in output
                assert "Guitar Tablature" in output

    def test_demo_chords_command(self):
        """Running demo-chords generates tablature."""
        with patch.object(sys, "argv", ["tabsynth", "demo-chords"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "Demo: Chord Events" in output

    def test_demo_mixed_command(self):
        """Running demo-mixed generates tablature."""
        with patch.object(sys, "argv", ["tabsynth", "demo-mixed"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "Demo: Mixed Notes and Chords" in output

    def test_unknown_command_exits_with_error(self):
        """Unknown command shows error and exits with code 1."""
        with patch.object(sys, "argv", ["tabsynth", "unknown-cmd"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with patch("sys.exit") as mock_exit:
                    main()
                    output = mock_stdout.getvalue()
                    assert "Unknown command: unknown-cmd" in output
                    mock_exit.assert_called_once_with(1)
