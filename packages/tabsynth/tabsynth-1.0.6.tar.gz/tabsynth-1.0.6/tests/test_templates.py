"""Tests for chord templates."""

import pytest
from tabsynth.templates import ChordTemplate, V1_TEMPLATES


def test_valid_chord_template():
    """Test creating a valid ChordTemplate."""
    template = ChordTemplate(
        id="test_chord",
        frets=[0, 2, 2, 1, 0, 0],
        barre=False,
        pitch_classes={"E", "G#", "B"},
        span=2,
        tags={"test"},
    )
    assert template.id == "test_chord"
    assert len(template.frets) == 6


def test_chord_template_invalid_frets_length():
    """Test ChordTemplate rejects wrong number of frets."""
    with pytest.raises(ValueError, match="frets must have exactly 6 elements"):
        ChordTemplate(
            id="bad_chord",
            frets=[0, 2, 2],  # Only 3 frets
            barre=False,
            pitch_classes={"E"},
            span=2,
            tags=set(),
        )


def test_chord_template_too_many_frets():
    """Test ChordTemplate rejects too many frets."""
    with pytest.raises(ValueError, match="frets must have exactly 6 elements"):
        ChordTemplate(
            id="bad_chord",
            frets=[0, 2, 2, 1, 0, 0, 3],  # 7 frets
            barre=False,
            pitch_classes={"E"},
            span=2,
            tags=set(),
        )


def test_v1_templates_valid():
    """Test that all V1 templates are valid."""
    assert len(V1_TEMPLATES) > 0
    for template in V1_TEMPLATES:
        assert len(template.frets) == 6
        assert isinstance(template.id, str)
        assert isinstance(template.pitch_classes, set)


def test_v1_templates_have_expected_chords():
    """Test V1 templates contain expected common chords."""
    ids = {t.id for t in V1_TEMPLATES}
    # Check for some essential open chords
    assert "E_major_open" in ids
    assert "A_major_open" in ids
    assert "D_major_open" in ids
    assert "G_major_open" in ids
    assert "C_major_open" in ids
    # Check for minor chords
    assert "E_minor_open" in ids
    assert "A_minor_open" in ids
