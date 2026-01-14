"""Custom exception classes for Wafer.

Tiger Style: Specific exceptions for clear error handling.
- Each exception type represents a specific failure mode
- All messages are constructed in the exception class
- Caller just passes the relevant data
"""

from pathlib import Path

# Configuration and module loading errors


class ResearchRootNotFoundError(RuntimeError):
    """Could not find research root directory."""

    def __init__(self, start_path: str) -> None:
        super().__init__(
            f"Could not find research root starting from {start_path}. " "Expected to find 'wafer_utils' directory."
        )
        self.start_path = start_path


class BenchmarkNameInferenceError(ValueError):
    """Cannot infer benchmark name from path."""

    def __init__(self, path: str) -> None:
        super().__init__(
            f"Cannot infer benchmark name from path: {path}. "
            "Expected path containing 'benchmarks/{{name}}/' or config in benchmark directory."
        )
        self.path = path


class SpecLoadError(RuntimeError):
    """Failed to load importlib spec from file."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Failed to load spec from {path}")
        self.path = path


class SpecLoaderMissingError(RuntimeError):
    """Spec loaded but has no loader."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Spec has no loader: {path}")
        self.path = path


class ConfigAttributeMissingError(RuntimeError):
    """Config module missing required attribute."""

    def __init__(self, path: str, attribute: str = "config") -> None:
        super().__init__(f"Config module {path} missing '{attribute}' attribute")
        self.path = path
        self.attribute = attribute


# Remote deployment errors


class RemoteDeploymentError(RuntimeError):
    """Failed to setup remote environment."""

    def __init__(self, error_message: str) -> None:
        super().__init__(f"Failed to setup remote environment: {error_message}")
        self.error_message = error_message


# GPU errors


class GPUQueryError(RuntimeError):
    """Failed to query GPU information."""

    def __init__(self, stderr: str) -> None:
        super().__init__(f"Failed to query GPU: {stderr}")
        self.stderr = stderr


class UnexpectedGPUOutputError(RuntimeError):
    """nvidia-smi returned unexpected output format."""

    def __init__(self, stdout: str) -> None:
        super().__init__(f"Unexpected nvidia-smi output: {stdout}")
        self.stdout = stdout


# Cache errors


class CacheSaveError(RuntimeError):
    """Failed to save cache file."""

    def __init__(self, cache_path: str, original_error: Exception) -> None:
        super().__init__(f"Failed to save cache to {cache_path}: {original_error}")
        self.cache_path = cache_path
        self.original_error = original_error


class CacheCorruptedError(RuntimeError):
    """Cache file corrupted (hash mismatch)."""

    def __init__(self) -> None:
        super().__init__("Cache corrupted: metadata hash mismatch")


# Beam search errors


class NoCorrectKernelsError(RuntimeError):
    """No correct kernels in initial set for beam search."""

    def __init__(self) -> None:
        super().__init__("No correct kernels in initial set - cannot start beam search")


# Dataset errors


class DatasetNotFoundError(RuntimeError):
    """Dataset file not found."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Dataset not found: {path}")
        self.path = path


class UnsupportedDatasetFormatError(RuntimeError):
    """Dataset format not supported."""

    def __init__(self, suffix: str) -> None:
        super().__init__(f"Unsupported dataset format: {suffix} (expected .jsonl)")
        self.suffix = suffix


class InvalidDatasetFormatError(ValueError):
    """Dataset has invalid format."""

    def __init__(self, details: str) -> None:
        super().__init__(f"Invalid dataset format: {details}")
        self.details = details


class InvalidTestCasesFormatError(InvalidDatasetFormatError):
    """Test cases format is invalid."""

    def __init__(self, test_cases_arg: str, error: Exception) -> None:
        details = (
            f"test-cases must be a valid JSON file path or inline JSON string. "
            f"Got: {test_cases_arg}. Error: {error}"
        )
        super().__init__(details)
        self.test_cases_arg = test_cases_arg
        self.error = error


class MissingFieldError(ValueError):
    """Required field missing from data."""

    def __init__(self, field: str, context: str = "") -> None:
        msg = f"Missing required field: {field}"
        if context:
            msg += f" ({context})"
        super().__init__(msg)
        self.field = field
        self.context = context


# Environment and configuration validation errors


class MissingAPIKeyError(RuntimeError):
    """Required API key not found in environment."""

    def __init__(self, key_name: str) -> None:
        super().__init__(f"{key_name} must be set before launching the optimizer loop.")
        self.key_name = key_name


class JSONParseError(ValueError):
    """Failed to parse JSON from environment variable."""

    def __init__(self, env_var: str, error: Exception) -> None:
        super().__init__(f"Failed to parse {env_var} as JSON: {error}")
        self.env_var = env_var
        self.error = error


class MissingWorkspaceKeyError(ValueError):
    """Workspace configuration missing required key."""

    def __init__(self, entry: dict) -> None:
        super().__init__(f"Entry {entry} missing 'workspace'/'path' key.")
        self.entry = entry


class UnsupportedEntryTypeError(ValueError):
    """Unsupported entry type in configuration."""

    def __init__(self, env_var: str, entry: object) -> None:
        super().__init__(f"Unsupported entry type in {env_var}: {entry!r}")
        self.env_var = env_var
        self.entry = entry


class InvalidJSONStructureError(ValueError):
    """JSON structure doesn't match expected format."""

    def __init__(self, env_var: str, expected: str, got: str) -> None:
        super().__init__(f"{env_var} must be {expected}, got {got}")
        self.env_var = env_var
        self.expected = expected
        self.got = got


class InvalidModelValueError(ValueError):
    """Model value has invalid type."""

    def __init__(self, value: object) -> None:
        super().__init__(f"Model value must be string or null, got {value!r}")
        self.value = value


class WorkspaceNotFoundError(FileNotFoundError):
    """Workspace directory does not exist."""

    def __init__(self, workspace: Path) -> None:
        super().__init__(f"Workspace {workspace} does not exist.")
        self.workspace = workspace


# Kernel-specific errors


class ImplementationNotFoundError(ValueError):
    """Implementation file not found."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Implementation file not found: {path}")
        self.path = path


class UnknownTestSuiteError(ValueError):
    """Unknown test suite name."""

    def __init__(self, suite: str, valid_suites: list) -> None:
        super().__init__(f"Unknown test suite '{suite}'. Valid: {valid_suites}")
        self.suite = suite
        self.valid_suites = valid_suites


class MissingReferenceCodeError(ValueError):
    """Problem missing reference code."""

    def __init__(self, problem_id: str) -> None:
        super().__init__(f"Problem {problem_id} has no reference_code")
        self.problem_id = problem_id


class UnknownSuiteTypeError(ValueError):
    """Unknown suite type format."""

    def __init__(self, suite_type: str) -> None:
        super().__init__(
            f"Unknown suite_type: {suite_type}. "
            "Expected format: {{benchmark}}_correctness or {{benchmark}}_benchmark"
        )
        self.suite_type = suite_type


class MissingFunctionDefinitionError(ValueError):
    """Kernel code missing expected function definition."""

    def __init__(self, function_name: str) -> None:
        super().__init__(
            f"Kernel code must define a function named '{function_name}'.\n"
            f"Expected: def {function_name}(data):\n"
            "The LLM was explicitly instructed to use this name. "
            "If this error occurs, the prompt needs to be clearer."
        )
        self.function_name = function_name


class ReferenceKernelLoadError(ImportError):
    """Failed to load reference kernel."""

    def __init__(self, problem_id: str, error: Exception) -> None:
        super().__init__(f"Failed to load reference kernel for {problem_id}: {error}")
        self.problem_id = problem_id
        self.error = error


class MissingProfilerError(ValueError):
    """No profiler enabled."""

    def __init__(self) -> None:
        super().__init__("Must enable at least one profiler (--torch or --ncu)")


class ReferenceCacheNotFoundError(FileNotFoundError):
    """Reference cache file not found."""

    def __init__(self, cache_path: str, problem_id: str, test_suite: str) -> None:
        super().__init__(
            f"Reference cache not found: {cache_path}\n"
            "Generate cache with:\n"
            f"  python scripts/generate_reference_cache.py "
            f"--problem {problem_id} --test-suite {test_suite}"
        )
        self.cache_path = cache_path
        self.problem_id = problem_id
        self.test_suite = test_suite


class CacheLoadError(RuntimeError):
    """Failed to load cache file."""

    def __init__(self, cache_path: str, error: Exception) -> None:
        super().__init__(f"Failed to load cache {cache_path}: {error}")
        self.cache_path = cache_path
        self.error = error


class CacheMissingFieldError(RuntimeError):
    """Cache missing required field."""

    def __init__(self, field: str, cache_path: str) -> None:
        super().__init__(f"Cache corrupted: missing {field} in {cache_path}")
        self.field = field
        self.cache_path = cache_path


class CacheParameterMismatchError(RuntimeError):
    """Cache parameters don't match requested parameters."""

    def __init__(self, requested: dict, cached: dict) -> None:
        super().__init__(
            f"Cache parameter mismatch:\n"
            f"  Requested: m={requested.get('m')}, k={requested.get('k')}, "
            f"l={requested.get('l')}, seed={requested.get('seed')}\n"
            f"  Cached: {cached}"
        )
        self.requested = requested
        self.cached = cached


class GenerateInputImportError(ImportError):
    """Failed to import generate_input from reference_kernel.py."""

    def __init__(self, cwd: str, error: Exception) -> None:
        super().__init__(
            f"Could not import generate_input from reference_kernel.py in CWD ({cwd}): {error}\n"
            "Make sure the problem directory contains reference_kernel.py with a generate_input function."
        )
        self.cwd = cwd
        self.error = error


class ReferenceBenchmarkError(RuntimeError):
    """Reference kernel benchmark failed."""

    def __init__(self, reference_path: str, error: str) -> None:
        super().__init__(f"Reference '{reference_path}' benchmark failed: {error}")
        self.reference_path = reference_path
        self.error = error


class CudaVersionValueError(ValueError):
    """Invalid CUDA version format."""

    def __init__(self, version: str) -> None:
        super().__init__(f"cuda_version must be numeric (e.g., '12.8'), got: {version}")
        self.version = version


class ReferenceKernelNotFoundError(FileNotFoundError):
    """Reference kernel file not found."""

    def __init__(self, full_path: str, ref_path: str) -> None:
        super().__init__(
            f"Reference kernel not found: {full_path}\n" f"Expected at: {ref_path} (relative to research root)"
        )
        self.full_path = full_path
        self.ref_path = ref_path


class CacheFileNotFoundError(FileNotFoundError):
    """Cache file not found."""

    def __init__(self, cache_path: str) -> None:
        super().__init__(f"Cache not found: {cache_path}")
        self.cache_path = cache_path
