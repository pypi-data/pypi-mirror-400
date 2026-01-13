"""End-to-end pipeline for converting events to tablature."""

from typing import Literal
from tabsynth.model import Event
from tabsynth.templates import ChordTemplate, V1_TEMPLATES
from tabsynth.optimize import optimize_sequence
from tabsynth.render import render_ascii, render_json, render_compact


OutputFormat = Literal["ascii", "json", "compact"]


def events_to_tablature(
    events: list[Event],
    output_format: OutputFormat = "ascii",
    templates: list[ChordTemplate] = None,
    max_fret: int = 15,
    tolerance_cents: float = 50.0,
) -> str:
    """
    Convert a list of musical events to guitar tablature.

    This is the main end-to-end pipeline that:
    1. Generates candidates for each event
    2. Optimizes the sequence using DP/Viterbi
    3. Renders the result in the requested format

    Args:
        events: List of NoteEvent and/or ChordEvent objects
        output_format: Output format ("ascii", "json", or "compact")
        templates: Chord templates for matching (default: V1_TEMPLATES)
        max_fret: Maximum fret for note candidates
        tolerance_cents: Pitch matching tolerance in cents

    Returns:
        Tablature string in the requested format
    """
    if templates is None:
        templates = V1_TEMPLATES

    # Optimize the sequence
    optimal_states = optimize_sequence(
        events=events,
        templates=templates,
        max_fret=max_fret,
        tolerance_cents=tolerance_cents,
    )

    # Render in requested format
    if output_format == "ascii":
        return render_ascii(optimal_states)
    elif output_format == "json":
        return render_json(optimal_states)
    elif output_format == "compact":
        return render_compact(optimal_states)
    else:
        raise ValueError(f"Unknown output format: {output_format}")


class TabSynthPipeline:
    """
    Configurable pipeline for tablature synthesis.
    """

    def __init__(
        self,
        templates: list[ChordTemplate] = None,
        max_fret: int = 15,
        tolerance_cents: float = 50.0,
    ):
        """
        Initialize the pipeline with configuration.

        Args:
            templates: Chord templates for matching
            max_fret: Maximum fret for note candidates
            tolerance_cents: Pitch matching tolerance
        """
        self.templates = templates if templates is not None else V1_TEMPLATES
        self.max_fret = max_fret
        self.tolerance_cents = tolerance_cents

    def process(
        self, events: list[Event], output_format: OutputFormat = "ascii"
    ) -> str:
        """
        Process events through the pipeline.

        Args:
            events: List of musical events
            output_format: Desired output format

        Returns:
            Tablature string
        """
        return events_to_tablature(
            events=events,
            output_format=output_format,
            templates=self.templates,
            max_fret=self.max_fret,
            tolerance_cents=self.tolerance_cents,
        )

    def add_template(self, template: ChordTemplate) -> None:
        """Add a new chord template to the pipeline."""
        self.templates.append(template)

    def set_templates(self, templates: list[ChordTemplate]) -> None:
        """Replace all templates with a new list."""
        self.templates = templates
