"""Tests for wafer_core.tools.compiler module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from wafer_core.tools.compiler import (
    ARCH_FALLBACK,
    ARCH_MIN_CUDA_VERSION,
    ArchDetectResult,
    CompileResult,
    compile_cuda,
    detect_arch,
)


class TestArchDetectResult:
    """Tests for ArchDetectResult dataclass."""

    def test_creates_detected_result(self) -> None:
        result = ArchDetectResult(
            detected=True,
            arch="sm_90",
            compute_capability="9.0",
            gpu_name="NVIDIA H100",
            gpu_type="H100",
        )

        assert result.detected is True
        assert result.arch == "sm_90"
        assert result.compute_capability == "9.0"
        assert result.gpu_name == "NVIDIA H100"
        assert result.gpu_type == "H100"

    def test_creates_fallback_result(self) -> None:
        result = ArchDetectResult(
            detected=False,
            arch="sm_80",
            fallback_archs=["sm_90", "sm_89"],
        )

        assert result.detected is False
        assert result.arch == "sm_80"
        assert result.fallback_archs == ["sm_90", "sm_89"]


class TestCompileResult:
    """Tests for CompileResult dataclass."""

    def test_creates_success_result(self) -> None:
        result = CompileResult(
            success=True,
            ptx="// PTX code",
            sass="// SASS code",
            arch_used="sm_90",
            nvcc_path="/usr/local/cuda/bin/nvcc",
            nvcc_version="12.0",
        )

        assert result.success is True
        assert result.ptx == "// PTX code"
        assert result.sass == "// SASS code"
        assert result.arch_used == "sm_90"

    def test_creates_error_result(self) -> None:
        result = CompileResult(
            success=False,
            error="Compilation failed",
            stage="ptx",
        )

        assert result.success is False
        assert result.error == "Compilation failed"
        assert result.stage == "ptx"


class TestDetectArch:
    """Tests for detect_arch()."""

    @patch("subprocess.run")
    def test_detects_h100(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            stdout="9.0, NVIDIA H100 80GB HBM3\n",
            returncode=0,
        )

        result = detect_arch()

        assert result.detected is True
        assert result.arch == "sm_90"
        assert result.compute_capability == "9.0"
        assert result.gpu_name == "NVIDIA H100 80GB HBM3"
        assert result.gpu_type == "H100"

    @patch("subprocess.run")
    def test_detects_l4(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            stdout="8.9, NVIDIA L4\n",
            returncode=0,
        )

        result = detect_arch()

        assert result.detected is True
        assert result.arch == "sm_89"
        assert result.gpu_type == "L4"

    @patch("subprocess.run")
    def test_returns_fallback_when_nvidia_smi_fails(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = FileNotFoundError("nvidia-smi not found")

        result = detect_arch()

        assert result.detected is False
        assert result.arch == "sm_80"  # Default fallback
        assert len(result.fallback_archs) > 0


class TestCompileCuda:
    """Tests for compile_cuda()."""

    @patch("wafer_core.tools.compiler.find_nvcc")
    def test_returns_error_when_nvcc_not_found(self, mock_find_nvcc: MagicMock) -> None:
        mock_find_nvcc.return_value = None

        result = compile_cuda("/tmp/test.cu", "sm_90")

        assert result.success is False
        assert "NVCC Not Found" in (result.error or "")

    @patch("wafer_core.tools.compiler.find_nvcc")
    @patch("wafer_core.tools.compiler.get_nvcc_version")
    @patch("os.path.isfile")
    @patch("os.access")
    def test_returns_error_when_file_not_found(
        self,
        mock_access: MagicMock,
        mock_isfile: MagicMock,
        mock_version: MagicMock,
        mock_find_nvcc: MagicMock,
    ) -> None:
        mock_find_nvcc.return_value = "/usr/local/cuda/bin/nvcc"
        mock_version.return_value = "12.0"
        mock_isfile.return_value = True
        mock_access.return_value = True

        # Mock _check_arch_support to return True
        with patch("wafer_core.tools.compiler._check_arch_support", return_value=(True, None)):
            result = compile_cuda("/nonexistent/file.cu", "sm_90")

        assert result.success is False
        assert "File Not Found" in (result.error or "")


class TestConstants:
    """Tests for module constants."""

    def test_arch_min_cuda_version_has_entries(self) -> None:
        assert "sm_90" in ARCH_MIN_CUDA_VERSION
        assert "sm_80" in ARCH_MIN_CUDA_VERSION

    def test_arch_fallback_has_entries(self) -> None:
        assert "sm_100" in ARCH_FALLBACK
        assert ARCH_FALLBACK["sm_100"] == "sm_90"

