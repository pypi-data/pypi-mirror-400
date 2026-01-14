"""Type definitions for NVFP4 kernel testing.

Defines the input/output tensor types and test case structure
for NVFP4 block-scaled GEMV kernels.
"""

from dataclasses import dataclass
from typing import TypeAlias

import torch

from wafer_core.utils.exceptions import GenerateInputImportError

# Type aliases for kernel I/O
# Input: (a, b, scale_a, scale_b, scale_a_permuted, scale_b_permuted, c)
input_t: TypeAlias = tuple[
    torch.Tensor,  # a: [m, k, l] float4_e2m1fn_x2
    torch.Tensor,  # b: [1, k, l] float4_e2m1fn_x2
    torch.Tensor,  # scale_a: [m, k, l] float8_e4m3fn (CPU)
    torch.Tensor,  # scale_b: [1, k, l] float8_e4m3fn (CPU)
    torch.Tensor,  # scale_a_permuted: GPU version
    torch.Tensor,  # scale_b_permuted: GPU version
    torch.Tensor,  # c: [m, 1, l] float16 (output buffer)
]

# Output: Modified c tensor
output_t: TypeAlias = torch.Tensor  # [m, 1, l] float16


@dataclass(frozen=True)
class TestCase:
    """Single test case for kernel verification.

    Generic test case that holds arbitrary parameters.
    Immutable to follow single-assignment principle.
    """

    params: dict  # Test parameters (e.g., {'size': 1024, 'seed': 42})
    name: str  # Human-readable test name

    def __post_init__(self) -> None:
        """Validate test case parameters."""
        assert isinstance(self.params, dict), f"params must be dict, got {type(self.params)}"
        assert len(self.params) > 0, "params cannot be empty"
        assert len(self.name) > 0, "name cannot be empty"

    def generate(self) -> input_t:
        """Generate fresh test data each time (lazy evaluation).

        This ensures:
        - Kernels can't corrupt data for subsequent tests
        - Each benchmark gets fresh tensors
        - Cache behavior is realistic

        Returns:
            Fresh input tuple for this test case
        """
        import os
        import sys

        # Import generate_input from current directory
        # The reference_kernel.py should be in the current working directory
        # (evaluate.py sets CWD to the problem directory before running tests)
        try:
            sys.path.insert(0, os.getcwd())
            from reference_kernel import generate_input  # type: ignore[import-not-found]

            return generate_input(**self.params)
        except ImportError as e:
            raise GenerateInputImportError(os.getcwd(), e) from e

    def serialize(self) -> str:
        """Serialize test case parameters for logging.

        Returns:
            Human-readable string representation
        """
        # Format as key=value pairs
        return ", ".join(f"{k}={v}" for k, v in sorted(self.params.items()))
