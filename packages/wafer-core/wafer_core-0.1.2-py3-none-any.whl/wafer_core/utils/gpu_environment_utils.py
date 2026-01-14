"""Helper utilities for GPU code execution environments.

Pure functions for common environment patterns:
- Code extraction from messages
- Submission tracking
- Feedback message formatting

Used by benchmarks/leetgpu/environment.py and benchmarks/gpumode/kernel_environment.py

Tiger Style:
- Pure functions only (no classes, no state)
- Explicit inputs/outputs
- Immutable data structures
"""

import re
from collections.abc import Callable
from dataclasses import replace
from typing import Any, TypeVar

from wafer_core.rollouts.dtypes import AgentState, Message

# Generic type for submissions
T = TypeVar("T")


def extract_code_from_message(message: Message, languages: list[str] | None = None) -> str | None:
    """Extract code block from markdown message.

    Looks for ```language blocks and returns the code content.

    Args:
        message: Message potentially containing code
        languages: Accepted language tags (e.g., ["python", "cuda", "triton"])
                  If None, accepts any language tag or no tag

    Returns:
        Code content if found, None otherwise

    Example:
        >>> msg = Message(role="assistant", content="```python\\nprint('hello')\\n```")
        >>> code = extract_code_from_message(msg, languages=["python"])
        >>> assert code == "print('hello')"
    """
    if not message.content:
        return None

    # Tiger Style: Type narrowing for message.content
    # Message type from wafer_core.rollouts.dtypes has generic content field
    content = message.content
    assert isinstance(content, str), "Message content must be string for code extraction"

    # Build pattern based on allowed languages
    if languages:
        lang_pattern = "|".join(re.escape(lang) for lang in languages)
        pattern = rf"```(?:{lang_pattern})?\s*\n(.*?)```"
    else:
        # Accept any language tag or no tag
        pattern = r"```(?:\w+)?\s*\n(.*?)```"

    matches = re.findall(pattern, content, re.DOTALL)

    if matches:
        # Return last code block (most recent implementation)
        return matches[-1].strip()

    return None


def track_submission(
    submissions: list[T],
    new_submission: T,
    current_best: T | None,
    comparator: Callable[[T, T], bool],
) -> tuple[list[T], T | None, bool]:
    """Track new submission and update best.

    Pure function for submission tracking pattern.
    Returns updated state (does not mutate inputs).

    Args:
        submissions: Current list of submissions
        new_submission: New submission to add
        current_best: Current best submission (or None)
        comparator: Function that returns True if first arg is better than second
                   Signature: comparator(new, best) -> bool

    Returns:
        (updated_submissions, new_best, is_new_best): Updated lists and whether best changed

    Example:
        >>> def is_higher_score(new, best):
        ...     return new['score'] > best['score']
        >>> subs = [{'score': 0.5}]
        >>> new = {'score': 0.8}
        >>> updated, best, is_new = track_submission(subs, new, subs[0], is_higher_score)
        >>> assert is_new and best['score'] == 0.8
    """
    # Add to list (immutable append)
    updated_submissions = submissions + [new_submission]

    # Determine new best
    if current_best is None:
        new_best = new_submission
        is_new_best = True
    else:
        is_new_best = comparator(new_submission, current_best)
        new_best = new_submission if is_new_best else current_best

    return updated_submissions, new_best, is_new_best


def inject_feedback_message(
    state: AgentState, feedback_message: Message, metadata_updates: dict[str, Any] | None = None
) -> AgentState:
    """Inject feedback message into agent trajectory.

    Pure function for updating agent state with environment feedback.
    Common pattern across all GPU environments.

    Args:
        state: Current agent state
        feedback_message: Message to inject (typically role="user")
        metadata_updates: Optional metadata to merge into trajectory

    Returns:
        Updated agent state with feedback injected

    Example:
        >>> feedback = Message(role="user", content="Test passed!")
        >>> metadata = {"environment_state": {...}}
        >>> new_state = inject_feedback_message(state, feedback, metadata)
    """
    # Update trajectory messages
    updated_trajectory = replace(
        state.actor.trajectory,
        messages=[*state.actor.trajectory.messages, feedback_message],
    )

    # Merge metadata if provided
    if metadata_updates:
        updated_trajectory = replace(updated_trajectory, metadata={**updated_trajectory.metadata, **metadata_updates})

    # Update actor and state
    updated_actor = replace(state.actor, trajectory=updated_trajectory)
    return replace(state, actor=updated_actor)


def create_no_code_feedback() -> Message:
    """Create standard feedback message for when no code is found.

    Returns:
        User message prompting for code submission
    """
    return Message(
        role="user",
        content=(
            "⚠️  No code found in your response. "
            "Please provide your solution in a code block:\n\n"
            "```python\n# Your code here\n```"
        ),
    )


def format_error_feedback(attempt_number: int, error_message: str, include_details: bool = True) -> str:
    """Format compilation/execution error feedback.

    Args:
        attempt_number: Submission attempt number
        error_message: Error message from execution
        include_details: Whether to include full error in code block

    Returns:
        Formatted feedback string
    """
    if include_details:
        return f"""❌ **Submission {attempt_number} Failed**

Your code had errors:
```
{error_message}
```

Please fix these errors and try again."""
    else:
        return f"""❌ **Submission {attempt_number} Failed**

{error_message}

Please fix these errors and try again."""


def format_partial_success_feedback(attempt_number: int, passed: int, total: int, score: float) -> str:
    """Format partial correctness feedback.

    Args:
        attempt_number: Submission attempt number
        passed: Number of tests passed
        total: Total number of tests
        score: Correctness score (0.0 to 1.0)

    Returns:
        Formatted feedback string
    """
    return f"""⚠️  **Submission {attempt_number} Partially Correct**

Tests passed: {passed}/{total}
Correctness score: {score:.1%}

Some tests are failing. Please review and improve your solution."""


def format_success_feedback(attempt_number: int, passed: int, total: int, additional_metrics: str | None = None) -> str:
    """Format successful submission feedback.

    Args:
        attempt_number: Submission attempt number
        passed: Number of tests passed
        total: Total number of tests
        additional_metrics: Optional extra metrics to display (e.g., "Runtime: 10ms")

    Returns:
        Formatted feedback string
    """
    feedback = f"""✅ **Submission {attempt_number} Passed!**

All tests passed! ({passed}/{total})"""

    if additional_metrics:
        feedback += f"\n\n{additional_metrics}"

    feedback += "\n\nGreat work! Your solution is correct."

    return feedback


def select_best_submission(submissions: list[T], comparator: Callable[[T, T], bool]) -> T | None:
    """Find best submission from list using comparator.

    Pure function for finding optimal submission.

    Args:
        submissions: List of submissions
        comparator: Returns True if first arg is better than second

    Returns:
        Best submission, or None if list is empty

    Example:
        >>> subs = [{'score': 0.5}, {'score': 0.8}, {'score': 0.3}]
        >>> best = select_best_submission(subs, lambda a, b: a['score'] > b['score'])
        >>> assert best['score'] == 0.8
    """
    if not submissions:
        return None

    best = submissions[0]
    for submission in submissions[1:]:
        if comparator(submission, best):
            best = submission

    return best


def make_correctness_comparator() -> Callable[[dict, dict], bool]:
    """Create comparator that prioritizes correctness then performance.

    Returns comparator function for use with track_submission/select_best_submission.

    Comparison logic:
    1. Correctness first (all_correct > not all_correct)
    2. Then performance (higher speedup/lower runtime)

    Returns:
        Comparator function: comparator(new, best) -> bool

    Example:
        >>> comparator = make_correctness_comparator()
        >>> new = {'all_correct': True, 'speedup': 1.5}
        >>> old = {'all_correct': False, 'speedup': 2.0}
        >>> assert comparator(new, old)  # Correct beats faster
    """

    def comparator(new: dict, best: dict) -> bool:
        # Correctness first
        new_correct = new.get("all_correct", False)
        best_correct = best.get("all_correct", False)

        if new_correct and not best_correct:
            return True
        if not new_correct and best_correct:
            return False

        # Both correct or both incorrect - compare performance
        # Try speedup first (higher is better)
        if "speedup" in new and "speedup" in best:
            return new["speedup"] > best["speedup"]

        # Fallback to correctness_score (higher is better)
        new_score = new.get("correctness_score", 0.0)
        best_score = best.get("correctness_score", 0.0)
        return new_score > best_score

    return comparator
