"""DEPRECATED: Backend registry for NVFP4 kernel implementations.

This module is deprecated. Use file paths directly instead of the registry system.

Migration:
    Old: BACKENDS.register("name", kernel_fn, "desc", "language")
         kernel = BACKENDS["name"]

    New: kernel_fn = load_kernel_from_file("/path/to/kernel.py")
         result = kernel_fn(test_input)

Only KernelBackend Protocol is kept for type hints.
"""

from typing import Protocol

from wafer_core.utils.kernel_utils.task import input_t, output_t


class KernelBackend(Protocol):
    """Protocol for NVFP4 kernel implementations.

    All kernels must accept input_t and return output_t.
    Use this for type hints only - load kernels from files directly.
    """

    def __call__(self, data: input_t) -> output_t:
        """Execute the kernel.

        Args:
            data: Input tuple (a, b, scale_a, scale_b, scale_a_perm, scale_b_perm, c)

        Returns:
            Output tensor (modified c)
        """
        ...


# DEPRECATED: Registry system removed
# Use file paths directly: load_kernel_from_file(path) from wafer_core.utils.kernel_utils.evaluate
