"""Submission selection utilities for GPU benchmark environments.

Pure functions for computing best submissions across different benchmarks.

Tiger Style:
- Pure functions only (no classes, no state)
- Explicit inputs/outputs
- Works with both dict and object-based submissions
"""

from collections.abc import Callable
from typing import TypeVar

# Generic type for submissions (dict or dataclass)
T = TypeVar("T")


def compute_best_submission(submissions: list[dict]) -> dict | None:
    """Select best submission by correctness first, then performance.

    Criteria:
    1. Must be compiled
    2. Correctness first (all_correct > not all_correct)
    3. Then performance (higher geomean_speedup)

    Args:
        submissions: List of submission dicts with keys:
            - compiled: bool
            - all_correct: bool
            - geomean_speedup: float

    Returns:
        Best submission dict, or None if no valid submissions

    Example:
        >>> subs = [
        ...     {"compiled": True, "all_correct": False, "geomean_speedup": 2.0},
        ...     {"compiled": True, "all_correct": True, "geomean_speedup": 1.5},
        ... ]
        >>> best = compute_best_submission(subs)
        >>> assert best["all_correct"]  # Correctness beats performance
    """
    best = None

    for sub in submissions:
        # Skip failed compilations
        if not sub.get("compiled", False):
            continue

        # First valid submission becomes best
        if best is None:
            best = sub
        # Correct submission beats incorrect
        elif sub.get("all_correct", False) and not best.get("all_correct", False):
            best = sub
        # Same correctness level - compare performance
        elif sub.get("all_correct", False) == best.get("all_correct", False):
            if sub.get("geomean_speedup", 0) > best.get("geomean_speedup", 0):
                best = sub

    return best


def is_better_than_best(new_submission: dict, current_best: dict | None) -> bool:
    """Check if new submission is better than current best.

    Used for incremental tracking without recomputing over full list.

    Args:
        new_submission: New submission to compare
        current_best: Current best submission (or None)

    Returns:
        True if new submission should replace current best

    Example:
        >>> new = {"compiled": True, "all_correct": True, "geomean_speedup": 2.0}
        >>> old = {"compiled": True, "all_correct": False, "geomean_speedup": 3.0}
        >>> assert is_better_than_best(new, old)  # Correctness beats speed
    """
    # Skip failed compilations
    if not new_submission.get("compiled", False):
        return False

    # First valid submission
    if current_best is None:
        return True

    new_correct = new_submission.get("all_correct", False)
    best_correct = current_best.get("all_correct", False)

    # Correctness first
    if new_correct and not best_correct:
        return True
    if not new_correct and best_correct:
        return False

    # Same correctness - compare performance
    new_speedup = new_submission.get("geomean_speedup", 0)
    best_speedup = current_best.get("geomean_speedup", 0)
    return new_speedup > best_speedup


def compute_best_submission_generic(submissions: list[T], comparator: Callable[[T, T], bool]) -> T | None:
    """Generic best submission selector with custom comparator.

    Useful for custom submission types (dataclasses, objects) or
    different selection criteria.

    Args:
        submissions: List of submissions (any type)
        comparator: Function that returns True if first arg is better than second
                   Signature: comparator(new, current_best) -> bool

    Returns:
        Best submission, or None if list is empty

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class Sub:
        ...     score: float
        >>> subs = [Sub(0.5), Sub(0.9), Sub(0.3)]
        >>> best = compute_best_submission_generic(subs, lambda a, b: a.score > b.score)
        >>> assert best.score == 0.9
    """
    if not submissions:
        return None

    best = submissions[0]
    for submission in submissions[1:]:
        if comparator(submission, best):
            best = submission

    return best


def track_and_update_best(
    current_submissions: list[dict], new_submission: dict, current_best: dict | None
) -> tuple[list[dict], dict | None, bool]:
    """Add submission and update best in one operation.

    Pure function - returns updated state without mutating inputs.

    Args:
        current_submissions: Current list of submissions
        new_submission: New submission to add
        current_best: Current best submission (or None)

    Returns:
        Tuple of (updated_submissions, new_best, is_new_best)
        - updated_submissions: New list with submission added
        - new_best: Updated best submission
        - is_new_best: True if new submission became the best

    Example:
        >>> subs = [{"compiled": True, "all_correct": False, "geomean_speedup": 1.5}]
        >>> new = {"compiled": True, "all_correct": True, "geomean_speedup": 1.2}
        >>> updated, best, is_new = track_and_update_best(subs, new, subs[0])
        >>> assert is_new and best["all_correct"]
    """
    # Add to list (immutable append)
    updated_submissions = current_submissions + [new_submission]

    # Check if new submission is best
    is_new_best = is_better_than_best(new_submission, current_best)
    new_best = new_submission if is_new_best else current_best

    return updated_submissions, new_best, is_new_best
