"""Cost functions for evaluating transitions between playable states."""

from tabsynth.model import PlayableState


def hand_position_cost(state1: PlayableState, state2: PlayableState) -> float:
    """
    Calculate the cost of moving between two hand positions.
    Based on the change in mean fret position.

    Args:
        state1: Starting playable state
        state2: Ending playable state

    Returns:
        Cost value (higher = more difficult transition)
    """
    fret_distance = abs(state2.mean_fret - state1.mean_fret)

    # Weight large jumps more heavily
    if fret_distance > 5:
        return fret_distance * 2.0
    elif fret_distance > 3:
        return fret_distance * 1.5
    else:
        return fret_distance


def string_change_cost(state1: PlayableState, state2: PlayableState) -> float:
    """
    Calculate the cost of changing strings.

    Args:
        state1: Starting playable state
        state2: Ending playable state

    Returns:
        Cost value based on string changes
    """
    # Count how many different strings are used
    common_strings = state1.strings & state2.strings
    total_strings = state1.strings | state2.strings

    # Reward overlap, penalize complete changes
    if not common_strings:
        return len(total_strings) * 0.5
    else:
        different_strings = len(total_strings) - len(common_strings)
        return different_strings * 0.3


def stretch_cost(state: PlayableState) -> float:
    """
    Calculate the cost of finger stretch for a single state.
    Based on the span between min and max frets.

    Args:
        state: The playable state to evaluate

    Returns:
        Cost value for the stretch required
    """
    span = state.max_fret - state.min_fret

    # Penalize large stretches
    if span > 4:
        return (span - 4) * 2.0
    elif span > 3:
        return (span - 3) * 1.0
    else:
        return 0.0


def barre_cost(state: PlayableState) -> float:
    """
    Calculate the cost penalty for barre chords.

    Args:
        state: The playable state to evaluate

    Returns:
        Cost value for barre requirement
    """
    return 2.0 if state.requires_barre else 0.0


def position_preference_cost(state: PlayableState) -> float:
    """
    Prefer lower positions (closer to headstock) slightly.

    Args:
        state: The playable state to evaluate

    Returns:
        Cost value favoring lower fret positions
    """
    # Small penalty for higher positions
    return state.mean_fret * 0.1


def transition_cost(state1: PlayableState, state2: PlayableState) -> float:
    """
    Calculate the total transition cost between two playable states.
    Combines multiple cost factors.

    Args:
        state1: Starting playable state
        state2: Ending playable state

    Returns:
        Total transition cost
    """
    cost = 0.0

    # Hand position movement
    cost += hand_position_cost(state1, state2)

    # String changes
    cost += string_change_cost(state1, state2)

    # Stretch cost for destination state
    cost += stretch_cost(state2)

    # Barre cost for destination state
    cost += barre_cost(state2)

    # Position preference
    cost += position_preference_cost(state2)

    return cost


def state_cost(state: PlayableState) -> float:
    """
    Calculate the intrinsic cost of a single playable state.
    Used for the first state in a sequence.

    Args:
        state: The playable state to evaluate

    Returns:
        Intrinsic cost of the state
    """
    cost = 0.0

    cost += stretch_cost(state)
    cost += barre_cost(state)
    cost += position_preference_cost(state)

    return cost
