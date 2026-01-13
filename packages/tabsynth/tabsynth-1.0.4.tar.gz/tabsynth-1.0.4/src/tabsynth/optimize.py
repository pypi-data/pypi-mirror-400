"""Dynamic programming / Viterbi optimization for finding optimal playable state sequences."""

from typing import Optional
from tabsynth.model import Event, PlayableState
from tabsynth.candidates import generate_candidates
from tabsynth.cost import state_cost, transition_cost
from tabsynth.templates import ChordTemplate


def optimize_sequence(
    events: list[Event],
    templates: list[ChordTemplate] = None,
    max_fret: int = 15,
    tolerance_cents: float = 50.0,
) -> list[PlayableState]:
    """
    Find the optimal sequence of playable states for a list of events.
    Uses dynamic programming (Viterbi-style) to minimize total cost.

    Args:
        events: List of NoteEvent or ChordEvent objects in temporal order
        templates: Chord templates for matching (default: V1_TEMPLATES)
        max_fret: Maximum fret for note candidates
        tolerance_cents: Pitch matching tolerance in cents

    Returns:
        Optimal sequence of PlayableState objects
    """
    if not events:
        return []

    # Generate candidates for each event
    all_candidates = []
    for event in events:
        candidates = generate_candidates(
            event,
            templates=templates,
            max_fret=max_fret,
            tolerance_cents=tolerance_cents,
        )
        if not candidates:
            # No valid candidates for this event - this shouldn't happen with reasonable tolerance
            # but we handle it by skipping this event
            continue
        all_candidates.append(candidates)

    if not all_candidates:
        return []

    # DP tables
    num_stages = len(all_candidates)

    # Initialize for first stage
    min_cost = {}  # min_cost[stage][candidate_idx] = (cost, prev_idx)
    min_cost[0] = {}

    for idx, candidate in enumerate(all_candidates[0]):
        min_cost[0][idx] = (state_cost(candidate), None)

    # Forward pass: compute minimum cost to reach each state
    for stage in range(1, num_stages):
        min_cost[stage] = {}

        for curr_idx, curr_candidate in enumerate(all_candidates[stage]):
            best_cost = float("inf")
            best_prev = None

            # Try all previous candidates
            for prev_idx, prev_candidate in enumerate(all_candidates[stage - 1]):
                prev_total_cost, _ = min_cost[stage - 1][prev_idx]
                trans_cost = transition_cost(prev_candidate, curr_candidate)
                total_cost = prev_total_cost + trans_cost

                if total_cost < best_cost:
                    best_cost = total_cost
                    best_prev = prev_idx

            min_cost[stage][curr_idx] = (best_cost, best_prev)

    # Backward pass: reconstruct optimal path
    # Find best final state
    final_stage = num_stages - 1
    best_final_idx = None
    best_final_cost = float("inf")

    for idx, (cost, _) in min_cost[final_stage].items():
        if cost < best_final_cost:
            best_final_cost = cost
            best_final_idx = idx

    if best_final_idx is None:
        # Fallback: return first candidate of each stage
        return [candidates[0] for candidates in all_candidates]

    # Backtrack to build path
    path_indices = []
    current_idx = best_final_idx

    for stage in range(final_stage, -1, -1):
        path_indices.append(current_idx)
        _, prev_idx = min_cost[stage][current_idx]
        current_idx = prev_idx

    path_indices.reverse()

    # Convert indices to actual PlayableState objects
    optimal_path = []
    for stage, idx in enumerate(path_indices):
        optimal_path.append(all_candidates[stage][idx])

    return optimal_path


def optimize_single_event(
    event: Event,
    templates: list[ChordTemplate] = None,
    max_fret: int = 15,
    tolerance_cents: float = 50.0,
) -> Optional[PlayableState]:
    """
    Find the best playable state for a single event.

    Args:
        event: A NoteEvent or ChordEvent
        templates: Chord templates for matching
        max_fret: Maximum fret for note candidates
        tolerance_cents: Pitch matching tolerance

    Returns:
        Best PlayableState or None if no candidates
    """
    candidates = generate_candidates(
        event, templates=templates, max_fret=max_fret, tolerance_cents=tolerance_cents
    )

    if not candidates:
        return None

    # Select candidate with minimum intrinsic cost
    best_candidate = None
    best_cost = float("inf")

    for candidate in candidates:
        cost = state_cost(candidate)
        if cost < best_cost:
            best_cost = cost
            best_candidate = candidate

    return best_candidate
