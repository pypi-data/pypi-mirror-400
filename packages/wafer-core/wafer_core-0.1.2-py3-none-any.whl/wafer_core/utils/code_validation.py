"""Code validation utilities for GPU kernel environments.

Pure functions for validating language-specific requirements (imports, decorators, etc.).

Tiger Style:
- Pure functions only (no classes, no state)
- Explicit validation rules
- Clear error messages
"""


def check_imports(code: str, language: str) -> tuple[bool, list[str]]:
    """Check for required imports based on language.

    Args:
        code: Code to validate
        language: Language identifier ("cute", "cuda", "pytorch", etc.)

    Returns:
        Tuple of (has_all_imports, missing_imports)

    Example:
        >>> code = "import torch\\ndef solve(): pass"
        >>> ok, missing = check_imports(code, "pytorch")
        >>> assert ok
    """
    missing = []

    if language == "cute":
        if "import cutlass" not in code:
            missing.append("import cutlass")
        if "cutlass.cute" not in code:
            missing.append("import cutlass.cute as cute")
        # Accept either from_dlpack or make_ptr - both are valid tensor creation patterns
        if "from_dlpack" not in code and "make_ptr" not in code:
            missing.append("from cutlass.cute.runtime import from_dlpack (or make_ptr)")
    elif language == "cuda":
        if "load_inline" not in code:
            missing.append("from torch.utils.cpp_extension import load_inline")

    return len(missing) == 0, missing


def check_decorators(code: str, language: str) -> tuple[bool, list[str]]:
    """Check for required decorators based on language.

    Args:
        code: Code to validate
        language: Language identifier ("cute", "cuda", "pytorch", etc.)

    Returns:
        Tuple of (has_all_decorators, missing_decorators)

    Example:
        >>> code = "@cute.jit\\n@cute.kernel\\ndef solve(): pass"
        >>> ok, missing = check_decorators(code, "cute")
        >>> assert ok
    """
    missing = []

    if language == "cute":
        if "@cute.jit" not in code and "@jit" not in code:
            missing.append("@cute.jit (required for CuteDSL wrapper function)")
        if "@cute.kernel" not in code and "@kernel" not in code:
            missing.append("@cute.kernel (required for GPU kernel definition)")

    return len(missing) == 0, missing


def validate_language_requirements(code: str, language: str) -> tuple[bool, str]:
    """Validate that code meets all language-specific requirements.

    Combines import and decorator checks into single validation.

    Args:
        code: Code to validate
        language: Language identifier ("cute", "cuda", "pytorch", etc.)

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if all requirements met
        - error_message: Empty string if valid, error details if invalid

    Example:
        >>> code = "import cutlass\\n@cute.jit\\ndef solve(): pass"
        >>> is_valid, error = validate_language_requirements(code, "cute")
        >>> if not is_valid:
        ...     print(f"Validation failed: {error}")
    """
    # No validation for general languages
    if language not in ["cute", "cuda"]:
        return True, ""

    errors = []

    # Level 1: Import checks
    has_imports, missing_imports = check_imports(code, language)
    if not has_imports:
        import_list = "\n  - ".join(missing_imports)
        errors.append(f"Missing required imports:\n  - {import_list}")

    # Level 2: Decorator checks (critical for CuteDSL)
    if language == "cute":
        has_decorators, missing_decorators = check_decorators(code, language)
        if not has_decorators:
            decorator_list = "\n  - ".join(missing_decorators)
            errors.append(f"Missing required decorators:\n  - {decorator_list}")

    if errors:
        return False, "\n\n".join(errors)

    return True, ""


def create_validation_error_result(error_message: str, language: str) -> dict:
    """Create standardized error result dict for validation failures.

    Args:
        error_message: Validation error message
        language: Language that failed validation

    Returns:
        Dict in standard evaluation result format

    Example:
        >>> result = create_validation_error_result("Missing imports", "cuda")
        >>> assert not result["compiled"]
        >>> assert "CUDA" in result["error_message"]
    """
    return {
        "compiled": False,
        "error_message": (
            f"Language requirement validation failed:\n\n{error_message}\n\n"
            f"Please ensure your code uses the required {language.upper()} patterns."
        ),
        "correctness_score": 0.0,
        "all_correct": False,
        "passed_tests": 0,
        "total_tests": 0,
        "geomean_speedup": 0.0,
    }
