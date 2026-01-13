"""End-to-end tests for the complete pipeline."""

import pytest
import json
from tabsynth.model import NoteEvent, ChordEvent
from tabsynth.pipeline import events_to_tablature, TabSynthPipeline
from tabsynth.templates import V1_TEMPLATES, ChordTemplate


def test_events_to_tablature_notes():
    """Test end-to-end conversion of notes to tablature."""
    events = [
        NoteEvent(pitch_hz=329.63, start=0.0, duration=0.5),
        NoteEvent(pitch_hz=369.99, start=0.5, duration=0.5),
        NoteEvent(pitch_hz=392.00, start=1.0, duration=0.5),
        NoteEvent(pitch_hz=440.00, start=1.5, duration=0.5),
    ]

    # ASCII output
    tab = events_to_tablature(events, output_format="ascii")
    assert isinstance(tab, str)
    assert len(tab) > 0
    assert "Guitar Tablature" in tab or "e|" in tab or "E|" in tab

    # JSON output
    json_tab = events_to_tablature(events, output_format="json")
    assert isinstance(json_tab, str)
    parsed = json.loads(json_tab)
    assert len(parsed) == 4

    # Compact output
    compact = events_to_tablature(events, output_format="compact")
    assert isinstance(compact, str)
    assert len(compact) > 0


def test_events_to_tablature_chords():
    """Test end-to-end conversion of chords to tablature."""
    events = [
        ChordEvent(pitches_hz=[329.63, 415.30, 493.88], start=0.0, duration=1.0),
        ChordEvent(pitches_hz=[440.00, 554.37, 659.26], start=1.0, duration=1.0),
    ]

    tab = events_to_tablature(events, output_format="ascii")
    assert isinstance(tab, str)
    assert len(tab) > 0


def test_events_to_tablature_mixed():
    """Test end-to-end conversion of mixed events."""
    events = [
        ChordEvent(pitches_hz=[329.63, 415.30, 493.88], start=0.0, duration=1.0),
        NoteEvent(pitch_hz=440.0, start=1.0, duration=0.5),
        NoteEvent(pitch_hz=493.88, start=1.5, duration=0.5),
    ]

    tab = events_to_tablature(events, output_format="ascii")
    assert isinstance(tab, str)
    assert len(tab) > 0


def test_pipeline_class():
    """Test the TabSynthPipeline class."""
    pipeline = TabSynthPipeline()

    events = [
        NoteEvent(pitch_hz=440.0, start=0.0, duration=0.5),
        NoteEvent(pitch_hz=493.88, start=0.5, duration=0.5),
    ]

    result = pipeline.process(events, output_format="compact")
    assert isinstance(result, str)
    assert len(result) > 0


def test_pipeline_custom_templates():
    """Test pipeline with custom templates."""
    custom_template = ChordTemplate(
        id="custom_chord",
        frets=[0, 0, 0, 0, 0, 0],
        barre=False,
        pitch_classes={"E", "A", "D", "G", "B"},
        span=0,
        tags={"custom"},
    )

    pipeline = TabSynthPipeline(templates=[custom_template])
    assert len(pipeline.templates) == 1

    # Add another template
    pipeline.add_template(V1_TEMPLATES[0])
    assert len(pipeline.templates) == 2


def test_ascii_output_structure():
    """Test that ASCII output has expected structure."""
    events = [
        NoteEvent(pitch_hz=440.0, start=0.0, duration=0.5),
    ]

    tab = events_to_tablature(events, output_format="ascii")

    # Should contain string labels
    lines = tab.split("\n")
    assert len(lines) > 0

    # Look for string indicators
    tab_lower = tab.lower()
    assert "e|" in tab_lower or "guitar" in tab_lower


def test_json_output_structure():
    """Test that JSON output has expected structure."""
    events = [
        NoteEvent(pitch_hz=440.0, start=0.0, duration=0.5),
        NoteEvent(pitch_hz=493.88, start=0.5, duration=0.5),
    ]

    json_tab = events_to_tablature(events, output_format="json")
    parsed = json.loads(json_tab)

    # Should be a list
    assert isinstance(parsed, list)
    assert len(parsed) == 2

    # Each entry should have expected fields
    for entry in parsed:
        assert "start" in entry
        assert "duration" in entry
        assert "kind" in entry
        assert "strings" in entry
        assert "frets" in entry


def test_empty_events():
    """Test handling of empty event list."""
    tab = events_to_tablature([], output_format="ascii")
    assert isinstance(tab, str)


def test_invalid_output_format():
    """Test handling of invalid output format."""
    events = [NoteEvent(pitch_hz=440.0, start=0.0, duration=0.5)]

    with pytest.raises(ValueError):
        events_to_tablature(events, output_format="invalid")


def test_pipeline_reproducibility():
    """Test that pipeline produces consistent results."""
    events = [
        NoteEvent(pitch_hz=440.0, start=0.0, duration=0.5),
        NoteEvent(pitch_hz=493.88, start=0.5, duration=0.5),
    ]

    result1 = events_to_tablature(events, output_format="json")
    result2 = events_to_tablature(events, output_format="json")

    # Should produce identical results
    assert result1 == result2
