"""Target selection logic for routing operations to targets.

Tiger Style:
- Pure functions (no side effects)
- Explicit preferences (hardcoded for Phase 1-5)
- Simple capability checking

Selection preferences (Phase 5: Modal + VM + Baremetal):
- NCU profiling: Must use baremetal with ncu_available=True
- Benchmarks: Prefer Modal (fast) → VM → Baremetal (stable hardware)
- Correctness: Prefer Modal (fast/cheap) → VM → Baremetal
- Torch profiling: Prefer Modal → VM → Baremetal
"""

from typing import Literal

from wafer_core.utils.kernel_utils.targets.config import (
    BaremetalTarget,
    ModalTarget,
    TargetConfig,
    VMTarget,
)


def select_target_for_operation(
    operation: Literal["correctness", "benchmark", "torch_profile", "ncu_profile"],
    available_targets: list[TargetConfig],
) -> TargetConfig | None:
    """Pick best target for this operation based on capabilities and preferences.

    Tiger Style: Pure function, explicit error handling.

    Args:
        operation: What operation to run
        available_targets: List of available targets to choose from

    Returns:
        Selected target, or None if no capable target available

    Example:
        targets = [lambda_vm, vultr_baremetal]
        target = select_target_for_operation("ncu_profile", targets)
        # Returns vultr_baremetal (only one with ncu_available=True)
    """
    # Filter to capable targets
    capable = [t for t in available_targets if _supports(t, operation)]

    if not capable:
        return None

    # Apply preference rules (Phase 5: Modal + VM + Baremetal)
    if operation == "ncu_profile":
        # NCU requires baremetal with ncu_available=True
        # Modal and VM don't support NCU (no privileged access)
        return next(
            (t for t in capable if isinstance(t, BaremetalTarget) and t.ncu_available),
            None,
        )

    elif operation == "benchmark":
        # Prefer Modal (fast cold start) → VM → Baremetal (save for profiling)
        # Modal targets are checked for availability during selection
        modal = [t for t in capable if isinstance(t, ModalTarget)]
        if modal:
            return modal[0]

        vm = [t for t in capable if isinstance(t, VMTarget)]
        if vm:
            return vm[0]

        baremetal = [t for t in capable if isinstance(t, BaremetalTarget)]
        return baremetal[0] if baremetal else capable[0]

    elif operation == "correctness" or operation == "torch_profile":
        # Prefer Modal (fast/cheap) → VM → Baremetal
        modal = [t for t in capable if isinstance(t, ModalTarget)]
        if modal:
            return modal[0]

        vm = [t for t in capable if isinstance(t, VMTarget)]
        if vm:
            return vm[0]

        # Last resort: baremetal (save for profiling if possible)
        return capable[0]

    else:
        # Unknown operation - return first capable target
        return capable[0]


def _supports(target: TargetConfig, operation: str) -> bool:
    """Check if target supports this operation.

    Tiger Style: Explicit capability checking.

    Args:
        target: Target to check
        operation: Operation to check support for

    Returns:
        True if target supports operation, False otherwise
    """
    if operation == "ncu_profile":
        # NCU requires baremetal with ncu_available=True
        return isinstance(target, BaremetalTarget) and target.ncu_available

    # All targets support correctness, benchmark, torch_profile
    # (assumes SSH access and GPU availability)
    return True
