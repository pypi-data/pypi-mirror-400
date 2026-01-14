"""Problem configuration loader for wafer wevin.

Loads problem definitions from YAML files or CLI arguments.
Generates system/user prompts from templates.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# ── Default Prompt Templates ─────────────────────────────────────────────────

DEFAULT_SYSTEM_PROMPT = """\
You are an expert GPU kernel developer specializing in high-performance computing for NVIDIA {gpu_type}.

You have one tool available:
- **write_kernel(filepath, code)**: Write a kernel file and automatically test it on remote GPU. Returns correctness and performance feedback.

**Workflow:**
1. Write your kernel implementation using write_kernel("kernel.py", code)
2. Review the test results (correctness tests + benchmark speedup)
3. Iterate based on feedback until you achieve the target performance

Each call to write_kernel automatically:
- Writes the file to the workspace
- Runs correctness tests against the reference
- Runs performance benchmarks
- Returns detailed results with any errors

**CRITICAL REQUIREMENT:** Your kernel function MUST be named exactly `custom_kernel`. The evaluation system will look for this specific function name.

**Language:** You MUST use {language} for your implementation.

**Key Requirements:**
1. Function MUST be named `custom_kernel`
2. Use {language} (required)
3. Target {speedup_target}x+ speedup vs reference
4. All correctness tests must pass

**Development Strategy:**
- Start with a simple correct implementation
- Submit and iterate based on test feedback
- Optimize for performance after correctness passes\
"""

DEFAULT_USER_MESSAGE = """\
**Problem: {problem_id}**

{problem_description}

**Reference Implementation:**
```python
{reference_code}
```

**Test Cases:** {test_summary}

**Benchmark Cases:** {benchmark_summary}

**Goal:** Achieve {speedup_target}x+ speedup vs reference while maintaining correctness!

**Requirements:**
- Your kernel function MUST be named `custom_kernel`
- Match the reference kernel's interface exactly

Start by writing your kernel implementation!\
"""


# ── Data Classes ─────────────────────────────────────────────────────────────


@dataclass
class ProblemConfig:
    """Configuration for a kernel optimization problem."""

    # Required
    problem_id: str
    problem_description: str
    reference_code: str
    tests: list[dict[str, Any]]
    benchmarks: list[dict[str, Any]]

    # Optional with defaults
    model: str = "claude-sonnet-4-5-20250929"
    temperature: float = 0.2
    max_tokens: int = 8192
    max_turns: int = 10
    speedup_target: float = 2.0
    gpu_type: str = "B200"
    language: str = "pytorch"  # or "cute" for CuteDSL

    # Custom prompts (f-string templates)
    system_prompt: str | None = None
    user_message: str | None = None

    # Target configuration
    target: str | None = None  # Target name or None for default

    # Computed fields
    _reference_path: Path | None = field(default=None, repr=False)

    def get_system_prompt(self) -> str:
        """Generate system prompt from template."""
        template = self.system_prompt or DEFAULT_SYSTEM_PROMPT
        return template.format(
            problem_id=self.problem_id,
            problem_description=self.problem_description,
            reference_code=self.reference_code,
            gpu_type=self.gpu_type,
            speedup_target=self.speedup_target,
            language=self.language,
            test_summary=self._format_cases(self.tests),
            benchmark_summary=self._format_cases(self.benchmarks),
        )

    def get_user_message(self) -> str:
        """Generate user message from template."""
        template = self.user_message or DEFAULT_USER_MESSAGE
        return template.format(
            problem_id=self.problem_id,
            problem_description=self.problem_description,
            reference_code=self.reference_code,
            gpu_type=self.gpu_type,
            speedup_target=self.speedup_target,
            language=self.language,
            test_summary=self._format_cases(self.tests),
            benchmark_summary=self._format_cases(self.benchmarks),
        )

    def _format_cases(self, cases: list[dict[str, Any]]) -> str:
        """Format test/benchmark cases for display."""
        if not cases:
            return "None"
        return ", ".join(str(c) for c in cases)

    def to_sample_data(self) -> dict[str, Any]:
        """Convert to sample_data dict for GPUModeSimpleEnvironment."""
        return {
            "problem_id": self.problem_id,
            "problem_description": self.problem_description,
            "reference_code": self.reference_code,
            "tests": self.tests,
            "benchmarks": self.benchmarks,
            "test_suite": "gpumode_correctness",
            "benchmark_suite": "gpumode_benchmark",
            "reference_backend": "reference",
            "gpu_type": self.gpu_type,
            "language": self.language,
        }


# ── Loaders ──────────────────────────────────────────────────────────────────


def load_problem_config(path: str | Path) -> tuple[ProblemConfig | None, str | None]:
    """Load problem configuration from YAML file.

    Args:
        path: Path to YAML config file

    Returns:
        (ProblemConfig, None) on success, (None, error) on failure
    """
    path = Path(path)

    if not path.exists():
        return None, f"Config file not found: {path}"

    if path.suffix not in (".yaml", ".yml"):
        return None, f"Expected .yaml or .yml file, got: {path.suffix}"

    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return None, f"Invalid YAML: {e}"

    return _parse_config(data, base_dir=path.parent)


def _parse_config(data: dict[str, Any], base_dir: Path) -> tuple[ProblemConfig | None, str | None]:
    """Parse config dict into ProblemConfig."""
    # Extract problem section
    problem = data.get("problem", {})
    if not problem:
        return None, "Missing 'problem' section"

    problem_id = problem.get("id")
    if not problem_id:
        return None, "Missing 'problem.id'"

    problem_description = problem.get("description", "")

    # Load reference code
    reference = data.get("reference")
    if not reference:
        return None, "Missing 'reference' (path to reference kernel)"

    reference_path = base_dir / reference
    if not reference_path.exists():
        return None, f"Reference file not found: {reference_path}"

    reference_code = reference_path.read_text()

    # Load test cases
    tests = data.get("tests", [])
    if not tests:
        return None, "Missing 'tests' (list of test case dicts)"

    benchmarks = data.get("benchmarks", [])

    # Optional fields
    config = ProblemConfig(
        problem_id=problem_id,
        problem_description=problem_description,
        reference_code=reference_code,
        tests=tests,
        benchmarks=benchmarks,
        model=data.get("model", "claude-sonnet-4-5-20250929"),
        temperature=data.get("temperature", 0.2),
        max_tokens=data.get("max_tokens", 8192),
        max_turns=data.get("max_turns", 10),
        speedup_target=data.get("speedup_target", 2.0),
        gpu_type=data.get("gpu_type", "B200"),
        language=data.get("language", "pytorch"),
        system_prompt=data.get("system_prompt"),
        user_message=data.get("user_message"),
        target=data.get("target"),
    )
    config._reference_path = reference_path

    return config, None


def create_problem_config_from_cli(
    reference: str | Path,
    description: str,
    tests: list[dict[str, Any]],
    benchmarks: list[dict[str, Any]] | None = None,
    **kwargs: Any,
) -> tuple[ProblemConfig | None, str | None]:
    """Create ProblemConfig from CLI arguments.

    Args:
        reference: Path to reference kernel file
        description: Problem description
        tests: List of test case dicts
        benchmarks: List of benchmark case dicts (defaults to tests if not provided)
        **kwargs: Optional overrides (model, max_turns, etc.)

    Returns:
        (ProblemConfig, None) on success, (None, error) on failure
    """
    reference_path = Path(reference)
    if not reference_path.exists():
        return None, f"Reference file not found: {reference_path}"

    reference_code = reference_path.read_text()

    # Default problem_id from filename
    problem_id = kwargs.get("problem_id", reference_path.stem)

    config = ProblemConfig(
        problem_id=problem_id,
        problem_description=description,
        reference_code=reference_code,
        tests=tests,
        benchmarks=benchmarks or tests,  # Use tests as benchmarks if not specified
        model=kwargs.get("model", "claude-sonnet-4-5-20250929"),
        temperature=kwargs.get("temperature", 0.2),
        max_tokens=kwargs.get("max_tokens", 8192),
        max_turns=kwargs.get("max_turns", 10),
        speedup_target=kwargs.get("speedup_target", 2.0),
        gpu_type=kwargs.get("gpu_type", "B200"),
        language=kwargs.get("language", "pytorch"),
        system_prompt=kwargs.get("system_prompt"),
        user_message=kwargs.get("user_message"),
        target=kwargs.get("target"),
    )
    config._reference_path = reference_path

    return config, None


def parse_test_case(test_str: str) -> tuple[dict[str, Any] | None, str | None]:
    """Parse test case from CLI string.

    Supports formats:
    - "m=128,k=256,l=1" -> {"m": 128, "k": 256, "l": 1}
    - '{"m": 128, "k": 256}' -> {"m": 128, "k": 256}

    Returns:
        (dict, None) on success, (None, error) on failure
    """
    test_str = test_str.strip()

    # Try JSON first
    if test_str.startswith("{"):
        import json

        try:
            return json.loads(test_str), None
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON: {e}"

    # Parse key=value format
    result: dict[str, Any] = {}
    for pair in test_str.split(","):
        pair = pair.strip()
        if "=" not in pair:
            return None, f"Invalid format: {pair} (expected key=value)"

        key, value = pair.split("=", 1)
        key = key.strip()
        value = value.strip()

        # Try to parse as number
        try:
            if "." in value:
                result[key] = float(value)
            else:
                result[key] = int(value)
        except ValueError:
            result[key] = value  # Keep as string

    return result, None
