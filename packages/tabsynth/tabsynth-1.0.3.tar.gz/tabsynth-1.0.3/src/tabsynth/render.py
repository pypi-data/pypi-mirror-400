"""Rendering functions for converting optimized playable states to tablature."""

import json
from tabsynth.model import PlayableState


def render_ascii(states: list[PlayableState], width: int = 80) -> str:
    """
    Render a sequence of playable states as ASCII guitar tablature.

    Args:
        states: List of PlayableState objects in temporal order
        width: Maximum width of output (characters per line)

    Returns:
        ASCII tablature string
    """
    if not states:
        return ""

    # Build tablature lines for each string (1-6, high to low)
    lines = {i: [] for i in range(1, 7)}

    # String labels
    string_names = {1: "e", 2: "B", 3: "G", 4: "D", 5: "A", 6: "E"}

    for state in states:
        # For each string, add the fret or dash
        for string in range(1, 7):
            if string in state.frets_by_string:
                fret = state.frets_by_string[string]
                fret_str = str(fret)
            else:
                fret_str = "-"

            lines[string].append(fret_str)

    # Build output with line breaks if needed
    result_lines = []

    # Add a header
    if states:
        result_lines.append("Guitar Tablature")
        result_lines.append("=" * 40)
        result_lines.append("")

    # Format each string line
    for string in range(1, 7):
        string_label = string_names[string]
        frets_str = "-".join(lines[string])
        line = f"{string_label}|{frets_str}|"
        result_lines.append(line)

    result_lines.append("")

    # Add legend for chords if any
    chord_states = [s for s in states if s.chord_id]
    if chord_states:
        result_lines.append("Chords:")
        seen_chords = set()
        for state in chord_states:
            if state.chord_id and state.chord_id not in seen_chords:
                result_lines.append(f"  {state.chord_id}")
                seen_chords.add(state.chord_id)

    return "\n".join(result_lines)


def render_json(states: list[PlayableState]) -> str:
    """
    Render a sequence of playable states as JSON.

    Args:
        states: List of PlayableState objects

    Returns:
        JSON string representation
    """
    output = []

    for idx, state in enumerate(states):
        state_dict = {
            "index": idx,
            "start": state.start,
            "duration": state.duration,
            "kind": state.kind,
            "strings": sorted(list(state.strings)),
            "frets": {str(s): f for s, f in sorted(state.frets_by_string.items())},
            "mean_fret": round(state.mean_fret, 2),
            "min_fret": state.min_fret,
            "max_fret": state.max_fret,
            "requires_barre": state.requires_barre,
            "chord_id": state.chord_id,
        }
        output.append(state_dict)

    return json.dumps(output, indent=2)


def render_compact(states: list[PlayableState]) -> str:
    """
    Render a compact text representation of playable states.
    Useful for debugging and testing.

    Args:
        states: List of PlayableState objects

    Returns:
        Compact text representation
    """
    if not states:
        return "No states"

    lines = []
    for idx, state in enumerate(states):
        frets_str = ",".join(
            f"{s}:{f}" for s, f in sorted(state.frets_by_string.items())
        )

        if state.chord_id:
            desc = f"{state.chord_id} [{frets_str}]"
        else:
            desc = f"note [{frets_str}]"

        lines.append(f"{idx}: t={state.start:.2f} {desc}")

    return "\n".join(lines)


def format_tablature_section(
    states: list[PlayableState], measures_per_line: int = 4, beats_per_measure: int = 4
) -> str:
    """
    Format tablature with measure divisions.

    Args:
        states: List of PlayableState objects
        measures_per_line: Number of measures per line
        beats_per_measure: Number of beats per measure

    Returns:
        Formatted tablature with measure markers
    """
    # This is a simplified version - could be enhanced with timing
    return render_ascii(states)
