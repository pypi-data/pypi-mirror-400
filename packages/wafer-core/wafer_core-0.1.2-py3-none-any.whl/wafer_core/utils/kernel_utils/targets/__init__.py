"""Pluggable target system for kernel evaluation.

Allows routing kernel operations (correctness, benchmark, profiling) to different
execution targets based on capabilities and preferences.

Example usage:
    from wafer_core.utils.kernel_utils.targets import BaremetalTarget, VMTarget, ModalTarget

    # Declare available targets
    modal = ModalTarget(
        name="modal-b200",
        modal_app_name="kernel-eval-b200",
        gpu_type="B200",
    )

    vm = VMTarget(
        name="lambda-vm",
        ssh_target="ubuntu@150.136.217.70:22",
        ssh_key="~/.ssh/lambda-mac",
        gpu_ids=[7],
    )

    baremetal = BaremetalTarget(
        name="vultr-baremetal",
        ssh_target="chiraag@45.76.244.62:22",
        ssh_key="~/.ssh/id_ed25519",
        gpu_ids=[6, 7],
        ncu_available=True,
    )

    available_targets = [modal, vm, baremetal]

    # System automatically routes operations:
    # - Correctness → modal (prefer fast/cheap serverless)
    # - Benchmarks → modal → vm → baremetal
    # - NCU profiling → baremetal (only one with ncu_available=True)
"""

from wafer_core.utils.kernel_utils.targets.config import (
    BaremetalTarget,
    ModalTarget,
    TargetConfig,
    VMTarget,
    is_baremetal_target,
    is_modal_target,
    is_vm_target,
    target_to_deployment_config,
)
from wafer_core.utils.kernel_utils.targets.execution import (
    check_target_available,
    find_free_gpu,
    run_operation_on_target,
)
from wafer_core.utils.kernel_utils.targets.selection import select_target_for_operation

__all__ = [
    "BaremetalTarget",
    "VMTarget",
    "ModalTarget",
    "TargetConfig",
    "is_baremetal_target",
    "is_vm_target",
    "is_modal_target",
    "target_to_deployment_config",
    "select_target_for_operation",
    "check_target_available",
    "find_free_gpu",
    "run_operation_on_target",
]
