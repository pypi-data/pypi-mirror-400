"""Tests for wafer_core.tools.tool_finder module."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

from wafer_core.tools.tool_finder import (
    NVCC_PATHS,
    NVDISASM_PATHS,
    find_nvcc,
    find_nvdisasm,
    get_install_command,
    get_nvcc_version,
    get_platform,
)


class TestGetPlatform:
    """Tests for get_platform()."""

    @patch("platform.system")
    def test_returns_linux_for_linux(self, mock_system: MagicMock) -> None:
        mock_system.return_value = "Linux"
        assert get_platform() == "linux"

    @patch("platform.system")
    def test_returns_darwin_for_macos(self, mock_system: MagicMock) -> None:
        mock_system.return_value = "Darwin"
        assert get_platform() == "darwin"

    @patch("platform.system")
    def test_returns_windows_for_windows(self, mock_system: MagicMock) -> None:
        mock_system.return_value = "Windows"
        assert get_platform() == "windows"


class TestFindNvcc:
    """Tests for find_nvcc()."""

    @patch("shutil.which")
    def test_finds_nvcc_in_path(self, mock_which: MagicMock) -> None:
        mock_which.return_value = "/usr/local/cuda/bin/nvcc"
        result = find_nvcc()
        assert result == "/usr/local/cuda/bin/nvcc"

    @patch("shutil.which")
    @patch("os.path.isfile")
    @patch("os.access")
    def test_finds_nvcc_at_known_path(
        self, mock_access: MagicMock, mock_isfile: MagicMock, mock_which: MagicMock
    ) -> None:
        mock_which.return_value = None
        mock_isfile.side_effect = lambda p: p == "/usr/local/cuda/bin/nvcc"
        mock_access.return_value = True

        with patch("wafer_core.tools.tool_finder.get_platform", return_value="linux"):
            result = find_nvcc()

        # Should find at known path
        assert result is not None

    @patch("shutil.which")
    @patch("os.path.isfile")
    @patch("os.path.isdir")
    def test_returns_none_when_not_found(
        self, mock_isdir: MagicMock, mock_isfile: MagicMock, mock_which: MagicMock
    ) -> None:
        mock_which.return_value = None
        mock_isfile.return_value = False
        mock_isdir.return_value = False

        result = find_nvcc()
        assert result is None


class TestFindNvdisasm:
    """Tests for find_nvdisasm()."""

    @patch("shutil.which")
    @patch("os.path.isfile")
    @patch("os.access")
    def test_finds_nvdisasm_at_known_path(
        self, mock_access: MagicMock, mock_isfile: MagicMock, mock_which: MagicMock
    ) -> None:
        mock_which.return_value = None
        mock_isfile.side_effect = lambda p: p == "/usr/local/cuda/bin/nvdisasm"
        mock_access.return_value = True

        with patch("wafer_core.tools.tool_finder.get_platform", return_value="linux"):
            result = find_nvdisasm()

        assert result == "/usr/local/cuda/bin/nvdisasm"


class TestGetNvccVersion:
    """Tests for get_nvcc_version()."""

    @patch("subprocess.run")
    def test_parses_version_from_output(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            stdout="nvcc: NVIDIA (R) Cuda compiler driver\n"
            "Cuda compilation tools, release 12.0, V12.0.140\n",
            returncode=0,
        )

        result = get_nvcc_version("/usr/local/cuda/bin/nvcc")
        assert result == "12.0"

    @patch("subprocess.run")
    def test_returns_none_on_error(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.TimeoutExpired("nvcc", 10)

        result = get_nvcc_version("/usr/local/cuda/bin/nvcc")
        assert result is None


class TestGetInstallCommand:
    """Tests for get_install_command()."""

    @patch("shutil.which")
    def test_returns_apt_command_for_debian(self, mock_which: MagicMock) -> None:
        mock_which.side_effect = lambda cmd: cmd == "apt-get"

        with patch("wafer_core.tools.tool_finder.get_platform", return_value="linux"):
            result = get_install_command()

        assert "apt" in result

    @patch("shutil.which")
    def test_returns_download_link_for_darwin(self, mock_which: MagicMock) -> None:
        mock_which.return_value = None

        with patch("wafer_core.tools.tool_finder.get_platform", return_value="darwin"):
            result = get_install_command()

        assert "developer.nvidia.com" in result


class TestConstants:
    """Tests for module constants."""

    def test_nvcc_paths_has_linux_entries(self) -> None:
        assert "linux" in NVCC_PATHS
        assert len(NVCC_PATHS["linux"]) > 0

    def test_nvdisasm_paths_has_linux_entries(self) -> None:
        assert "linux" in NVDISASM_PATHS
        assert len(NVDISASM_PATHS["linux"]) > 0

