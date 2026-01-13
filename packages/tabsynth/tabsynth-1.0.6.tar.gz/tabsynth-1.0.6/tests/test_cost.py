"""Tests for cost functions."""

import pytest
from tabsynth.model import PlayableState
from tabsynth.cost import (
    hand_position_cost,
    string_change_cost,
    stretch_cost,
    barre_cost,
    position_preference_cost,
    transition_cost,
    state_cost,
)


def _make_state(
    strings: set[int],
    frets: dict[int, int],
    requires_barre: bool = False,
) -> PlayableState:
    """Helper to create a PlayableState."""
    fret_vals = list(frets.values())
    return PlayableState(
        start=0.0,
        duration=0.5,
        kind="chord" if len(strings) > 1 else "note",
        strings=strings,
        frets_by_string=frets,
        mean_fret=sum(fret_vals) / len(fret_vals) if fret_vals else 0.0,
        min_fret=min(fret_vals) if fret_vals else 0,
        max_fret=max(fret_vals) if fret_vals else 0,
        requires_barre=requires_barre,
    )


class TestHandPositionCost:
    """Tests for hand_position_cost function."""

    def test_same_position(self):
        """No cost for same position."""
        s1 = _make_state({1}, {1: 5})
        s2 = _make_state({1}, {1: 5})
        assert hand_position_cost(s1, s2) == 0.0

    def test_small_move(self):
        """Small moves have linear cost."""
        s1 = _make_state({1}, {1: 5})
        s2 = _make_state({1}, {1: 7})
        cost = hand_position_cost(s1, s2)
        assert cost == 2.0  # 2 frets * 1.0

    def test_medium_move(self):
        """Moves 4-5 frets have 1.5x weight."""
        s1 = _make_state({1}, {1: 5})
        s2 = _make_state({1}, {1: 9})
        cost = hand_position_cost(s1, s2)
        assert cost == 4 * 1.5  # 4 frets * 1.5

    def test_large_move(self):
        """Moves > 5 frets have 2x weight."""
        s1 = _make_state({1}, {1: 0})
        s2 = _make_state({1}, {1: 10})
        cost = hand_position_cost(s1, s2)
        assert cost == 10 * 2.0  # 10 frets * 2.0


class TestStringChangeCost:
    """Tests for string_change_cost function."""

    def test_same_strings(self):
        """No cost for same strings."""
        s1 = _make_state({1, 2}, {1: 5, 2: 5})
        s2 = _make_state({1, 2}, {1: 7, 2: 7})
        assert string_change_cost(s1, s2) == 0.0

    def test_complete_string_change(self):
        """Complete string change has higher cost."""
        s1 = _make_state({1, 2}, {1: 5, 2: 5})
        s2 = _make_state({5, 6}, {5: 0, 6: 0})
        cost = string_change_cost(s1, s2)
        assert cost == 4 * 0.5  # 4 different strings * 0.5

    def test_partial_string_change(self):
        """Partial string overlap has lower cost."""
        s1 = _make_state({1, 2}, {1: 5, 2: 5})
        s2 = _make_state({2, 3}, {2: 5, 3: 5})
        cost = string_change_cost(s1, s2)
        # common: {2}, total: {1,2,3} = 3, different = 2
        assert cost == 2 * 0.3


class TestStretchCost:
    """Tests for stretch_cost function."""

    def test_no_stretch(self):
        """No cost for small spans."""
        state = _make_state({1, 2, 3}, {1: 0, 2: 1, 3: 2})  # span = 2
        assert stretch_cost(state) == 0.0

    def test_span_three(self):
        """No cost for span of 3."""
        state = _make_state({1, 2, 3}, {1: 0, 2: 1, 3: 3})  # span = 3
        assert stretch_cost(state) == 0.0

    def test_span_four(self):
        """Small cost for span of 4."""
        state = _make_state({1, 2}, {1: 0, 2: 4})  # span = 4
        cost = stretch_cost(state)
        assert cost == (4 - 3) * 1.0  # Line 69 coverage

    def test_large_stretch(self):
        """Higher cost for span > 4."""
        state = _make_state({1, 2}, {1: 0, 2: 6})  # span = 6
        cost = stretch_cost(state)
        assert cost == (6 - 4) * 2.0  # Line 67 coverage


class TestBarreCost:
    """Tests for barre_cost function."""

    def test_no_barre(self):
        """No cost without barre."""
        state = _make_state({1}, {1: 5}, requires_barre=False)
        assert barre_cost(state) == 0.0

    def test_with_barre(self):
        """Fixed cost for barre chords."""
        state = _make_state({1, 2, 3}, {1: 1, 2: 1, 3: 1}, requires_barre=True)
        assert barre_cost(state) == 2.0


class TestPositionPreferenceCost:
    """Tests for position_preference_cost function."""

    def test_low_position(self):
        """Low positions have low cost."""
        state = _make_state({1}, {1: 2})
        assert position_preference_cost(state) == pytest.approx(0.2)

    def test_high_position(self):
        """High positions have higher cost."""
        state = _make_state({1}, {1: 12})
        assert position_preference_cost(state) == pytest.approx(1.2)


class TestTransitionCost:
    """Tests for transition_cost function."""

    def test_combines_costs(self):
        """Transition cost combines all factors."""
        s1 = _make_state({1}, {1: 5})
        s2 = _make_state({2}, {2: 7})
        cost = transition_cost(s1, s2)
        # Should be > 0 (combines multiple cost functions)
        assert cost > 0


class TestStateCost:
    """Tests for state_cost function."""

    def test_simple_state(self):
        """State cost for simple note."""
        state = _make_state({1}, {1: 5})
        cost = state_cost(state)
        # Just position preference for a simple note
        assert cost == 0.5  # 5 * 0.1
