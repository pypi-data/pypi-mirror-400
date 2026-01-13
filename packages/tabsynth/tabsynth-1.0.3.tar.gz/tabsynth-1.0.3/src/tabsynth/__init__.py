"""
tabsynth - Guitar tablature synthesis from musical events.

This package converts pre-detected musical events (notes and chords) into
playable guitar tablature using candidate generation and dynamic programming
optimization.
"""

from tabsynth.model import (
    NoteEvent,
    ChordEvent,
    Event,
    PlayableState,
    PlayableKind,
)

from tabsynth.fretboard import (
    STANDARD_TUNING_HZ,
    NOTE_NAMES,
    build_fretboard,
    cents_diff,
    hz_to_midi,
    hz_to_pitch_class,
)

from tabsynth.templates import (
    ChordTemplate,
    V1_TEMPLATES,
)

from tabsynth.candidates import (
    generate_candidates,
    generate_note_candidates,
    generate_chord_candidates,
    match_chord_template,
)

from tabsynth.cost import (
    transition_cost,
    state_cost,
    hand_position_cost,
    string_change_cost,
    stretch_cost,
    barre_cost,
    position_preference_cost,
)

from tabsynth.optimize import (
    optimize_sequence,
    optimize_single_event,
)

from tabsynth.render import (
    render_ascii,
    render_json,
    render_compact,
    format_tablature_section,
)

from tabsynth.pipeline import (
    events_to_tablature,
    TabSynthPipeline,
    OutputFormat,
)

__version__ = "0.1.0"

__all__ = [
    # Models
    "NoteEvent",
    "ChordEvent",
    "Event",
    "PlayableState",
    "PlayableKind",
    # Fretboard
    "STANDARD_TUNING_HZ",
    "NOTE_NAMES",
    "build_fretboard",
    "cents_diff",
    "hz_to_midi",
    "hz_to_pitch_class",
    # Templates
    "ChordTemplate",
    "V1_TEMPLATES",
    # Candidates
    "generate_candidates",
    "generate_note_candidates",
    "generate_chord_candidates",
    "match_chord_template",
    # Cost
    "transition_cost",
    "state_cost",
    "hand_position_cost",
    "string_change_cost",
    "stretch_cost",
    "barre_cost",
    "position_preference_cost",
    # Optimize
    "optimize_sequence",
    "optimize_single_event",
    # Render
    "render_ascii",
    "render_json",
    "render_compact",
    "format_tablature_section",
    # Pipeline
    "events_to_tablature",
    "TabSynthPipeline",
    "OutputFormat",
]
