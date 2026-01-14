"""Reference kernel output caching for agent evaluation.

Provides utilities to load cached reference outputs during agent testing.
This decouples agent kernel execution from reference kernel execution,
preventing CUDA context contamination and enabling clear error attribution.

Tiger Style:
- Explicit cache validation
- Clear error messages on cache misses
- No silent failures
"""

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import torch

from wafer_core.utils.exceptions import (
    CacheCorruptedError,
    CacheLoadError,
    CacheMissingFieldError,
    CacheParameterMismatchError,
    ReferenceCacheNotFoundError,
)


def get_cache_key(problem_id: str, test_suite: str, m: int, k: int, l: int, seed: int) -> str:
    """Generate cache key from test parameters.

    Must match the key generation in scripts/generate_reference_cache.py.

    Args:
        problem_id: Problem identifier
        test_suite: Test suite name
        m, k, l, seed: Test case parameters

    Returns:
        Cache filename
    """
    return f"{problem_id}_{test_suite}_{m}_{k}_{l}_{seed}.pt"


def get_cache_dir(problem_id: str) -> Path:
    """Get cache directory for a problem.

    Args:
        problem_id: Problem identifier

    Returns:
        Path to .cache/reference_outputs/{problem_id}/
    """
    # Find project root (where .cache should be)
    current = Path(__file__).parent.parent
    cache_dir = current / ".cache" / "reference_outputs" / problem_id
    return cache_dir


def load_cached_reference(
    problem_id: str,
    test_suite: str,
    m: int,
    k: int,
    l: int,
    seed: int,
    validate_version: bool = True,
) -> tuple[tuple, torch.Tensor, dict]:
    """Load cached reference outputs for a test case.

    Args:
        problem_id: Problem identifier
        test_suite: Test suite name
        m, k, l, seed: Test case parameters
        validate_version: Warn if PyTorch version mismatch

    Returns:
        (reference_input, reference_output, metadata)

    Raises:
        FileNotFoundError: If cache doesn't exist
        RuntimeError: If cache is corrupted

    Example:
        >>> ref_input, ref_output, metadata = load_cached_reference(
        ...     "nvfp4_gemv_blackwell", "smoke", 128, 256, 1, 42
        ... )
        >>> # Now test agent kernel
        >>> agent_output = agent_kernel(ref_input)
        >>> is_correct = torch.allclose(agent_output, ref_output)
    """
    # Tiger Style: Assert preconditions
    assert problem_id, "problem_id cannot be empty"
    assert test_suite, "test_suite cannot be empty"
    assert m > 0, f"m must be positive, got {m}"
    assert k > 0, f"k must be positive, got {k}"
    assert l > 0, f"l must be positive, got {l}"

    # Get cache path
    cache_dir = get_cache_dir(problem_id)
    cache_key = get_cache_key(problem_id, test_suite, m, k, l, seed)
    cache_path = cache_dir / cache_key

    # Check if cache exists
    if not cache_path.exists():
        raise ReferenceCacheNotFoundError(str(cache_path), problem_id, test_suite)

    # Load cache
    try:
        # Use weights_only=False since we're loading our own trusted cache files
        # PyTorch 2.6+ changed the default to weights_only=True
        cache_data = torch.load(cache_path, weights_only=False)
    except Exception as e:
        raise CacheLoadError(str(cache_path), e) from e

    # Validate cache structure
    if "metadata" not in cache_data:
        raise CacheMissingFieldError("metadata", str(cache_path))
    if "reference_input" not in cache_data:
        raise CacheMissingFieldError("reference_input", str(cache_path))
    if "reference_output" not in cache_data:
        raise CacheMissingFieldError("reference_output", str(cache_path))

    metadata = cache_data["metadata"]

    # Validate metadata hash
    if "metadata_hash" in cache_data:
        expected_hash = compute_metadata_hash(metadata)
        actual_hash = cache_data["metadata_hash"]
        if expected_hash != actual_hash:
            raise CacheCorruptedError()

    # Validate test parameters match
    cached_params = metadata.get("test_params", {})
    if (
        cached_params.get("m") != m
        or cached_params.get("k") != k
        or cached_params.get("l") != l
        or cached_params.get("seed") != seed
    ):
        raise CacheParameterMismatchError({"m": m, "k": k, "l": l, "seed": seed}, cached_params)

    # Warn if PyTorch version changed
    if validate_version:
        cached_version = metadata.get("pytorch_version")
        current_version = torch.__version__
        if cached_version and cached_version != current_version:
            print(
                f"⚠️  Warning: Reference cache created with PyTorch {cached_version}, "
                f"current version is {current_version}"
            )
            print("   Consider regenerating cache if results seem incorrect")

    # Extract return values
    reference_input = cache_data["reference_input"]
    reference_output = cache_data["reference_output"]

    # Tiger Style: Assert postconditions on return values
    assert reference_input is not None, "Loaded reference_input is None"
    assert isinstance(reference_input, tuple), f"reference_input must be tuple, got {type(reference_input)}"
    assert len(reference_input) > 0, "reference_input is empty"

    assert reference_output is not None, "Loaded reference_output is None"
    assert isinstance(reference_output, torch.Tensor), f"reference_output must be Tensor, got {type(reference_output)}"

    assert metadata is not None, "Loaded metadata is None"
    assert isinstance(metadata, dict), f"metadata must be dict, got {type(metadata)}"
    assert "test_params" in metadata, "metadata missing test_params"

    return (reference_input, reference_output, metadata)


def compute_metadata_hash(metadata: dict) -> str:
    """Compute hash of metadata for validation.

    Args:
        metadata: Dict with test_params, versions, etc.

    Returns:
        SHA256 hash (first 16 chars)
    """
    # Sort keys for deterministic hashing
    metadata_str = json.dumps(metadata, sort_keys=True)
    return hashlib.sha256(metadata_str.encode()).hexdigest()[:16]


def check_cache_exists(problem_id: str, test_suite: str) -> tuple[bool, str]:
    """Check if reference cache exists for a test suite.

    Args:
        problem_id: Problem identifier
        test_suite: Test suite name

    Returns:
        (exists, message)
        - exists: True if cache directory exists and has .pt files
        - message: Descriptive message
    """
    cache_dir = get_cache_dir(problem_id)

    if not cache_dir.exists():
        return False, f"Cache directory does not exist: {cache_dir}"

    # Check for .pt files matching test suite
    cache_files = list(cache_dir.glob(f"{problem_id}_{test_suite}_*.pt"))

    if not cache_files:
        return False, f"No cache files found for test suite '{test_suite}' in {cache_dir}"

    return True, f"Found {len(cache_files)} cached test cases in {cache_dir}"


def generate_cache_entry(
    problem_id: str,
    test_suite: str,
    test_case: Any,  # TestCase object
    reference_backend: Callable,  # Backend callable
) -> None:
    """Generate a single cache entry for a test case.

    Args:
        problem_id: Problem identifier (e.g., "nvfp4_gemv_blackwell")
        test_suite: Test suite name
        test_case: TestCase object with m, k, l, seed, name
        reference_backend: Reference backend function to run
    """
    from datetime import datetime, timezone

    # Generate test data
    test_input = test_case.generate()

    # Run reference kernel
    reference_output = reference_backend(test_input)

    # Move output to CPU for caching
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    reference_output_cpu = reference_output.cpu()

    # Move input tensors to CPU
    def to_cpu(data: Any) -> Any:
        if isinstance(data, tuple):
            return tuple(to_cpu(x) for x in data)
        elif isinstance(data, list):
            return [to_cpu(x) for x in data]
        elif isinstance(data, dict):
            return {k: to_cpu(v) for k, v in data.items()}
        elif isinstance(data, torch.Tensor):
            return data.cpu()
        else:
            return data

    reference_input_cpu = to_cpu(test_input)

    # Prepare metadata
    metadata = {
        "test_params": {
            "m": test_case.m,
            "k": test_case.k,
            "l": test_case.l,
            "seed": test_case.seed,
            "name": test_case.name,
        },
        "pytorch_version": torch.__version__,
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "num_input_tensors": len(reference_input_cpu) if isinstance(reference_input_cpu, tuple) else 1,
        "output_shape": list(reference_output_cpu.shape),
        "output_dtype": str(reference_output_cpu.dtype),
    }

    # Package cache data
    cache_data = {
        "metadata": metadata,
        "metadata_hash": compute_metadata_hash(metadata),
        "reference_input": reference_input_cpu,
        "reference_output": reference_output_cpu,
    }

    # Save to disk
    cache_dir = get_cache_dir(problem_id)
    cache_dir.mkdir(parents=True, exist_ok=True)

    cache_key = get_cache_key(problem_id, test_suite, test_case.m, test_case.k, test_case.l, test_case.seed)
    cache_path = cache_dir / cache_key

    torch.save(cache_data, cache_path)
    print(f"   💾 Generated cache: {cache_key}")


def load_or_generate_cached_reference(
    problem_id: str,
    test_suite: str,
    test_case: Any,  # TestCase object
    reference_backend: Callable,  # Backend callable
    regenerate: bool = False,
) -> tuple[tuple, torch.Tensor, dict]:
    """Load cached reference, auto-generating if missing.

    This is the "smart" version of load_cached_reference that handles
    cache misses gracefully by generating cache on-the-fly.

    Args:
        problem_id: Problem identifier
        test_suite: Test suite name
        test_case: TestCase object with m, k, l, seed, name
        reference_backend: Reference backend function (for generation)
        regenerate: Force regenerate even if cache exists

    Returns:
        (reference_input, reference_output, metadata)
    """
    cache_dir = get_cache_dir(problem_id)
    cache_key = get_cache_key(problem_id, test_suite, test_case.m, test_case.k, test_case.l, test_case.seed)
    cache_path = cache_dir / cache_key

    # Check if we need to generate
    should_generate = regenerate or not cache_path.exists()

    if should_generate:
        if regenerate:
            print(f"   🔄 Regenerating cache (forced): {cache_key}")
        else:
            print(f"   📝 Cache miss - generating: {cache_key}")

        generate_cache_entry(problem_id, test_suite, test_case, reference_backend)

    # Now load the cache (either existing or just generated)
    return load_cached_reference(
        problem_id,
        test_suite,
        test_case.m,
        test_case.k,
        test_case.l,
        test_case.seed,
        validate_version=not regenerate,  # Skip version warning if we just generated
    )
