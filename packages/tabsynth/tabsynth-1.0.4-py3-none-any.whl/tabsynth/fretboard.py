"""Fretboard modeling and pitch helpers."""

import math

# Standard tuning frequencies (Hz) for strings 6 (lowest) to 1 (highest)
STANDARD_TUNING_HZ: dict[int, float] = {
    6: 82.4069,  # E2
    5: 110.0000,  # A2
    4: 146.8324,  # D3
    3: 195.9977,  # G3
    2: 246.9417,  # B3
    1: 329.6276,  # E4
}

# Note names in chromatic order
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def build_fretboard(
    open_string_hz: dict[int, float], max_fret: int = 24
) -> dict[int, dict[int, float]]:
    """
    Build a fretboard mapping of string -> fret -> pitch_hz.

    Args:
        open_string_hz: Dictionary mapping string number to open string frequency
        max_fret: Maximum fret number (default 24)

    Returns:
        Dictionary: fretboard[string][fret] = pitch_hz
    """
    fretboard = {}
    for string, open_hz in open_string_hz.items():
        fretboard[string] = {}
        for fret in range(max_fret + 1):
            # Equal temperament: each fret is a semitone (2^(1/12) ratio)
            pitch = open_hz * (2 ** (fret / 12))
            fretboard[string][fret] = pitch
    return fretboard


def cents_diff(a: float, b: float) -> float:
    """
    Calculate the pitch difference in cents between two frequencies.

    Args:
        a: First frequency in Hz
        b: Second frequency in Hz

    Returns:
        Difference in cents (1200 cents = 1 octave)
    """
    if a <= 0 or b <= 0:
        return float("inf")
    return 1200 * math.log2(a / b)


def hz_to_midi(hz: float) -> float:
    """
    Convert frequency in Hz to MIDI note number.

    Args:
        hz: Frequency in Hz

    Returns:
        MIDI note number (A440 = 69)
    """
    if hz <= 0:
        return 0.0
    return 69 + 12 * math.log2(hz / 440.0)


def hz_to_pitch_class(hz: float) -> str:
    """
    Convert frequency to pitch class name (C, C#, D, etc.).

    Args:
        hz: Frequency in Hz

    Returns:
        Pitch class name (one of NOTE_NAMES)
    """
    midi = hz_to_midi(hz)
    note_index = round(midi) % 12
    return NOTE_NAMES[note_index]
