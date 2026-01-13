"""Command-line interface for tabsynth."""

import sys
from tabsynth.model import NoteEvent, ChordEvent
from tabsynth.pipeline import events_to_tablature


def demo_notes():
    """Generate a simple demo with note events."""
    # Simple melody: E F# G A (ascending)
    events = [
        NoteEvent(pitch_hz=329.63, start=0.0, duration=0.5),  # E4
        NoteEvent(pitch_hz=369.99, start=0.5, duration=0.5),  # F#4
        NoteEvent(pitch_hz=392.00, start=1.0, duration=0.5),  # G4
        NoteEvent(pitch_hz=440.00, start=1.5, duration=0.5),  # A4
    ]
    return events


def demo_chords():
    """Generate a simple demo with chord events."""
    # E major, A major, E minor progression
    events = [
        ChordEvent(
            pitches_hz=[329.63, 392.00, 493.88],  # E G# B
            start=0.0,
            duration=1.0,
        ),
        ChordEvent(
            pitches_hz=[440.00, 554.37, 659.26],  # A C# E
            start=1.0,
            duration=1.0,
        ),
        ChordEvent(
            pitches_hz=[329.63, 392.00, 493.88],  # E G B
            start=2.0,
            duration=1.0,
        ),
    ]
    return events


def demo_mixed():
    """Generate a demo with mixed notes and chords."""
    events = [
        ChordEvent(
            pitches_hz=[329.63, 415.30, 493.88],  # E G# B
            start=0.0,
            duration=1.0,
        ),
        NoteEvent(pitch_hz=440.00, start=1.0, duration=0.5),  # A4
        NoteEvent(pitch_hz=493.88, start=1.5, duration=0.5),  # B4
        ChordEvent(
            pitches_hz=[440.00, 554.37, 659.26],  # A C# E
            start=2.0,
            duration=1.0,
        ),
    ]
    return events


def main():
    """Main CLI entry point."""
    args = sys.argv[1:]

    if not args or args[0] == "help":
        print("tabsynth - Guitar tablature synthesis from musical events")
        print()
        print("Usage:")
        print("  tabsynth demo-notes   - Demo with single notes")
        print("  tabsynth demo-chords  - Demo with chord events")
        print("  tabsynth demo-mixed   - Demo with mixed notes and chords")
        print("  tabsynth help         - Show this help")
        print()
        print("Examples:")
        print("  tabsynth demo-notes")
        print("  tabsynth demo-chords")
        return

    command = args[0]

    if command == "demo-notes":
        print("Demo: Single Notes")
        print("-" * 50)
        events = demo_notes()
        tab = events_to_tablature(events, output_format="ascii")
        print(tab)

    elif command == "demo-chords":
        print("Demo: Chord Events")
        print("-" * 50)
        events = demo_chords()
        tab = events_to_tablature(events, output_format="ascii")
        print(tab)

    elif command == "demo-mixed":
        print("Demo: Mixed Notes and Chords")
        print("-" * 50)
        events = demo_mixed()
        tab = events_to_tablature(events, output_format="ascii")
        print(tab)

    else:
        print(f"Unknown command: {command}")
        print("Run 'tabsynth help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
