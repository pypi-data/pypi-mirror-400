"""Modal backend execution for kernel evaluation.

Provides serverless GPU execution via Modal, matching the API of remote_execution.py.

Example usage:
    from wafer_core.utils.modal_execution import setup_modal_deployment, execute_kernel_modal

    # Setup Modal
    state, err = await setup_modal_deployment(
        modal_token_id="ak-xxx",
        modal_token_secret="as-xxx",
        gpu_type="B200",
    )

    # Execute kernel
    results = await execute_kernel_modal(
        modal_state=state,
        kernel_code=code,
        context=context,
        profiling_config=profiling_config,
    )
"""

from wafer_core.utils.modal_execution.modal_config import ModalConfig
from wafer_core.utils.modal_execution.modal_execution import (
    ModalDeploymentState,
    execute_kernel_modal,
    setup_modal_deployment,
)

__all__ = [
    "ModalConfig",
    "ModalDeploymentState",
    "setup_modal_deployment",
    "execute_kernel_modal",
]
