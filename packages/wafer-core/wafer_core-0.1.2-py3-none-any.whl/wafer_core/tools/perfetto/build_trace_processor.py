"""Build trace_processor from Perfetto source.

This module replaces the shell script build-trace-processor.sh with pure Python,
providing better integration, error handling, and cross-platform support.

Why Python over shell:
- No shell dependency (works on Windows too)
- Better error messages and logging
- Integrates with existing TraceProcessorManager
- Easier to maintain and debug

Build process:
1. Detect platform (mac/linux) and architecture (arm64/x64)
2. Generate GN build configuration (args.gn)
3. Apply patches for compatibility (zlib on macOS)
4. Run GN to generate ninja files
5. Build trace_processor_shell with ninja
6. Verify build includes required modules
7. Install binary to storage directory

Tiger Style:
- Explicit status reporting at each step
- Tuple returns for errors (result, error)
- Assertions for programmer errors
- Clear logging with actionable messages
"""

import logging
import platform
import re
import shutil
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BuildConfig:
    """Configuration for trace_processor build.
    
    WHY frozen=True: Build config is immutable once created.
    """
    perfetto_source_dir: Path
    storage_dir: Path
    ui_version: str | None = None


@dataclass(frozen=True)
class BuildResult:
    """Result of a build operation.
    
    WHY frozen=True: Result is a snapshot, immutable.
    """
    success: bool
    binary_path: str | None
    version: str | None
    error: str | None = None
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "binaryPath": self.binary_path,
            "version": self.version,
            "error": self.error,
        }


class TraceProcessorBuilder:
    """Builds trace_processor from Perfetto source.
    
    Responsibilities:
    - Platform/architecture detection
    - GN build configuration
    - Patch application (zlib for macOS)
    - Build execution via ninja
    - Binary verification and installation
    """
    
    def __init__(self, config: BuildConfig):
        """Initialize builder with configuration.
        
        Args:
            config: BuildConfig with source and target paths
        """
        assert config.perfetto_source_dir.exists(), f"Perfetto source not found: {config.perfetto_source_dir}"
        
        self.config = config
        self.perfetto_dir = config.perfetto_source_dir
        self.storage_dir = config.storage_dir
        
    def get_platform_info(self) -> tuple[str, str]:
        """Detect current platform and architecture.
        
        Returns:
            (platform, arch) tuple - e.g., ("mac", "arm64") or ("linux", "x64")
            
        Raises:
            ValueError: If platform is unsupported
        """
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Detect platform
        if system == "darwin":
            plat = "mac"
        elif system == "linux":
            plat = "linux"
        else:
            raise ValueError(f"Unsupported platform: {system}")
        
        # Detect architecture
        if machine in ("arm64", "aarch64"):
            arch = "arm64"
        elif machine in ("x86_64", "amd64", "x64"):
            arch = "x64"
        else:
            raise ValueError(f"Unsupported architecture: {machine}")
        
        return plat, arch

    def get_build_dir(self) -> Path:
        """Get the build output directory path.
        
        Returns:
            Path to build directory (e.g., out/mac-arm64)
        """
        plat, arch = self.get_platform_info()
        return self.perfetto_dir / "out" / f"{plat}-{arch}"

    def get_git_info(self) -> tuple[str | None, str | None]:
        """Get git commit hash and expected version from Perfetto source.
        
        Returns:
            (commit_hash, expected_version) - either may be None if unavailable
        """
        commit_hash = None
        expected_version = None
        
        # Get git commit hash
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short=9", "HEAD"],
                cwd=self.perfetto_dir,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                commit_hash = result.stdout.strip()
        except Exception as e:
            logger.warning(f"Could not get git commit hash: {e}")
        
        # Get expected version from write_version_header.py
        version_script = self.perfetto_dir / "tools" / "write_version_header.py"
        changelog = self.perfetto_dir / "CHANGELOG"
        
        if version_script.exists() and changelog.exists():
            try:
                result = subprocess.run(
                    ["python3", str(version_script), "--stdout", "--changelog", str(changelog)],
                    cwd=self.perfetto_dir,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    expected_version = result.stdout.strip()
            except Exception as e:
                logger.warning(f"Could not determine expected version: {e}")
        
        return commit_hash, expected_version

    def generate_gn_args(self, build_dir: Path) -> None:
        """Generate GN build configuration (args.gn).
        
        Args:
            build_dir: Path to build output directory
        """
        _, arch = self.get_platform_info()
        
        # Create build directory
        build_dir.mkdir(parents=True, exist_ok=True)
        
        # GN args content
        # WHY these specific args:
        # - is_debug=false: Optimized release build
        # - enable_perfetto_trace_processor_*: Include all required modules
        # - perfetto_build_standalone=true: Include all operators (window, etc.)
        # - perfetto_enable_git_rev_version_header=true: Include git hash in version
        # - extra_target_c*flags: Disable -Werror to allow build on various compilers
        args_content = f"""# Build configuration for trace_processor_shell
# Generated by wafer-core build_trace_processor.py

is_debug = false

# Enable trace processor with all required features
enable_perfetto_trace_processor = true
enable_perfetto_trace_processor_sqlite = true
enable_perfetto_trace_processor_httpd = true
enable_perfetto_trace_processor_json = true

# Standalone build mode for full feature set
perfetto_build_standalone = true
build_with_chromium = false
is_perfetto_build_generator = false

# Include git commit hash in version (critical for UI compatibility)
perfetto_enable_git_rev_version_header = true

# Disable warnings-as-errors to avoid build failures from compiler differences
extra_target_cxxflags = "-Wno-error -Wno-switch-default -Wno-macro-redefined"
extra_target_cflags = "-Wno-error -Wno-macro-redefined"

# Target CPU architecture
target_cpu = "{arch}"
"""
        
        args_file = build_dir / "args.gn"
        args_file.write_text(args_content)
        logger.info(f"Generated GN args at {args_file}")

    def clean_version_headers(self, build_dir: Path) -> None:
        """Clean version header files to force regeneration.
        
        WHY: Ensures git commit hash is included in new builds.
        
        Args:
            build_dir: Path to build output directory
        """
        # Version header can be at different locations depending on Perfetto version
        headers = [
            build_dir / "gen" / "perfetto_version.gen.h",
            build_dir / "gen" / "src" / "base" / "perfetto_version.gen.h",
        ]
        
        for header in headers:
            if header.exists():
                header.unlink()
                logger.info(f"Cleaned version header: {header}")

    def patch_zlib_for_macos(self) -> None:
        """Apply zlib patch for macOS compatibility.
        
        WHY: zlib tries to redefine fdopen() as a macro, which conflicts
        with macOS system headers. We comment out the problematic line.
        """
        if platform.system().lower() != "darwin":
            return
        
        zutil_path = self.perfetto_dir / "buildtools" / "zlib" / "zutil.h"
        if not zutil_path.exists():
            logger.warning(f"zutil.h not found at {zutil_path}, skipping patch")
            return
        
        content = zutil_path.read_text()
        
        # Look for the problematic fdopen macro
        problematic_line = "#        define fdopen(fd,mode) NULL"
        patched_line = "// #        define fdopen(fd,mode) NULL /* Disabled for macOS compatibility by wafer-core */"
        
        if problematic_line in content and patched_line not in content:
            content = content.replace(problematic_line, patched_line)
            zutil_path.write_text(content)
            logger.info("Patched zlib zutil.h for macOS fdopen() compatibility")
        elif patched_line in content:
            logger.debug("zlib zutil.h already patched")

    def run_gn_gen(self, build_dir: Path) -> tuple[bool, str | None]:
        """Run GN to generate ninja build files.
        
        Args:
            build_dir: Path to build output directory
            
        Returns:
            (True, None) on success, (False, error_message) on failure
        """
        gn_path = self.perfetto_dir / "tools" / "gn"
        
        if not gn_path.exists():
            return False, f"GN not found at {gn_path}. Run tools/install-build-deps first."
        
        logger.info(f"Running GN to generate build files in {build_dir}")
        
        try:
            result = subprocess.run(
                [str(gn_path), "gen", str(build_dir)],
                cwd=self.perfetto_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            if result.returncode != 0:
                return False, f"GN gen failed: {result.stderr[:500]}"
            
            return True, None
            
        except subprocess.TimeoutExpired:
            return False, "GN gen timed out (2 minute limit)"
        except Exception as e:
            return False, f"GN gen failed: {e}"

    def run_ninja_build(self, build_dir: Path) -> tuple[bool, str | None]:
        """Run ninja to build trace_processor_shell.
        
        Args:
            build_dir: Path to build output directory
            
        Returns:
            (True, None) on success, (False, error_message) on failure
        """
        ninja_path = self.perfetto_dir / "tools" / "ninja"
        
        if not ninja_path.exists():
            return False, f"Ninja not found at {ninja_path}. Run tools/install-build-deps first."
        
        logger.info("Building trace_processor_shell (this may take 5-10 minutes on first build)...")
        
        try:
            result = subprocess.run(
                [str(ninja_path), "-C", str(build_dir), "trace_processor_shell"],
                cwd=self.perfetto_dir,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )
            
            if result.returncode != 0:
                return False, f"Ninja build failed: {result.stderr[:500]}"
            
            return True, None
            
        except subprocess.TimeoutExpired:
            return False, "Ninja build timed out (10 minute limit)"
        except Exception as e:
            return False, f"Ninja build failed: {e}"

    def verify_binary(self, binary_path: Path) -> tuple[bool, str | None, str | None]:
        """Verify the built binary is valid and has required modules.
        
        Args:
            binary_path: Path to trace_processor_shell binary
            
        Returns:
            (is_valid, version, error_message)
        """
        if not binary_path.exists():
            return False, None, f"Binary not found at {binary_path}"
        
        # Make executable
        binary_path.chmod(binary_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        # Get version
        version = None
        try:
            result = subprocess.run(
                [str(binary_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            output = result.stdout + result.stderr
            
            # Try to match version with commit hash (e.g., v49.0-33a4fd078)
            match = re.search(r"v\d+\.\d+-[a-f0-9]+", output, re.IGNORECASE)
            if match:
                version = match.group(0)
            else:
                # Fallback to base version
                match = re.search(r"v\d+\.\d+", output, re.IGNORECASE)
                if match:
                    version = match.group(0)
                    logger.warning(f"Version {version} does not include git commit hash")
                    
        except Exception as e:
            logger.warning(f"Could not get binary version: {e}")
        
        # Verify window operator symbol (optional, nm may not be available)
        if shutil.which("nm"):
            try:
                result = subprocess.run(
                    ["nm", str(binary_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if "window_operator" in result.stdout.lower() or "windowoperatormodule" in result.stdout.lower():
                    logger.info("✓ Window operator module found in binary")
                else:
                    logger.warning("⚠ Window operator symbol not found in binary")
            except Exception:
                pass
        
        return True, version, None

    def install_binary(self, binary_path: Path) -> tuple[str, str | None]:
        """Install the built binary to storage directory.
        
        Args:
            binary_path: Path to built trace_processor_shell
            
        Returns:
            (installed_path, error_message)
        """
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = self.storage_dir / "trace_processor"
        
        # Copy binary
        shutil.copy2(binary_path, target_path)
        
        # Make executable
        target_path.chmod(target_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        logger.info(f"Installed trace_processor to {target_path}")
        
        # Log binary size
        size_mb = target_path.stat().st_size / (1024 * 1024)
        logger.info(f"Binary size: {size_mb:.1f} MB")
        
        return str(target_path), None

    def install_build_deps(self) -> tuple[bool, str | None]:
        """Install Perfetto build dependencies.
        
        Returns:
            (True, None) on success, (False, error_message) on failure
        """
        install_script = self.perfetto_dir / "tools" / "install-build-deps"
        
        if not install_script.exists():
            logger.warning(f"install-build-deps not found at {install_script}")
            return True, None  # Not fatal, continue anyway
        
        logger.info("Installing Perfetto build dependencies...")
        
        try:
            result = subprocess.run(
                [str(install_script)],
                cwd=self.perfetto_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            
            if result.returncode != 0:
                logger.warning(f"install-build-deps returned non-zero: {result.stderr[:200]}")
                # Don't fail - try to continue anyway
            
            return True, None
            
        except subprocess.TimeoutExpired:
            logger.warning("install-build-deps timed out (5 minute limit)")
            return True, None  # Don't fail, try to continue
        except Exception as e:
            logger.warning(f"install-build-deps failed: {e}")
            return True, None  # Don't fail, try to continue

    def verify_git_repository(self) -> tuple[bool, str | None]:
        """Verify Perfetto is a git repository (needed for version header).
        
        Returns:
            (True, None) if git repo, (False, error_message) otherwise
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.perfetto_dir,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode != 0:
                return False, "Perfetto is not a git repository. Version will not include commit hash."
            
            return True, None
            
        except Exception as e:
            return False, f"Could not verify git repository: {e}"

    def build(self) -> BuildResult:
        """Build trace_processor from source.
        
        This is the main entry point that orchestrates the entire build process.
        
        Returns:
            BuildResult with success status, binary path, version, and any errors
        """
        logger.info(f"Building trace_processor from {self.perfetto_dir}")
        
        try:
            plat, arch = self.get_platform_info()
            logger.info(f"Building for platform: {plat}/{arch}")
        except ValueError as e:
            return BuildResult(success=False, binary_path=None, version=None, error=str(e))
        
        # Step 1: Verify git repository
        is_git, git_warning = self.verify_git_repository()
        if not is_git:
            logger.warning(git_warning)
        
        # Step 2: Get git info for logging
        commit_hash, expected_version = self.get_git_info()
        if commit_hash:
            logger.info(f"Git commit: {commit_hash}")
        if expected_version:
            logger.info(f"Expected version (to match UI): {expected_version}")
        
        # Step 3: Install build dependencies
        self.install_build_deps()
        
        # Step 4: Get build directory
        build_dir = self.get_build_dir()
        
        # Step 5: Generate GN args
        self.generate_gn_args(build_dir)
        
        # Step 6: Clean version headers to force regeneration
        self.clean_version_headers(build_dir)
        
        # Step 7: Apply patches
        self.patch_zlib_for_macos()
        
        # Step 8: Run GN gen
        success, err = self.run_gn_gen(build_dir)
        if not success:
            return BuildResult(success=False, binary_path=None, version=None, error=err)
        
        # Step 9: Run ninja build
        success, err = self.run_ninja_build(build_dir)
        if not success:
            return BuildResult(success=False, binary_path=None, version=None, error=err)
        
        # Step 10: Verify binary
        built_binary = build_dir / "trace_processor_shell"
        is_valid, version, err = self.verify_binary(built_binary)
        if not is_valid:
            return BuildResult(success=False, binary_path=None, version=None, error=err)
        
        # Check version compatibility with UI
        if version and expected_version and version != expected_version:
            if version.split("-")[0] == expected_version.split("-")[0]:
                logger.info(f"✓ Base version matches ({version.split('-')[0]})")
            else:
                logger.warning(f"⚠ Version mismatch: built {version}, expected {expected_version}")
        elif version:
            logger.info(f"✓ Built trace_processor version: {version}")
        
        # Step 11: Install binary
        installed_path, err = self.install_binary(built_binary)
        if err:
            return BuildResult(success=False, binary_path=None, version=version, error=err)
        
        logger.info("✓ Successfully built and installed trace_processor")
        
        return BuildResult(
            success=True,
            binary_path=installed_path,
            version=version,
        )


def build_trace_processor(
    perfetto_source_dir: str,
    storage_dir: str,
    ui_version: str | None = None,
) -> tuple[str | None, str | None]:
    """Build trace_processor from Perfetto source.
    
    Convenience function that wraps TraceProcessorBuilder.
    
    Args:
        perfetto_source_dir: Path to Perfetto source directory
        storage_dir: Directory to install trace_processor binary
        ui_version: Optional expected UI version for compatibility checking
        
    Returns:
        (binary_path, None) on success, (None, error_message) on failure
    """
    config = BuildConfig(
        perfetto_source_dir=Path(perfetto_source_dir),
        storage_dir=Path(storage_dir),
        ui_version=ui_version,
    )
    
    builder = TraceProcessorBuilder(config)
    result = builder.build()
    
    if result.success:
        return result.binary_path, None
    else:
        return None, result.error


# CLI interface for standalone testing
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Build trace_processor from Perfetto source")
    parser.add_argument("perfetto_source", help="Path to Perfetto source directory")
    parser.add_argument("--storage-dir", "-s", default=str(Path.home() / ".wafer" / "perfetto"),
                        help="Directory to install trace_processor")
    parser.add_argument("--ui-version", help="Expected Perfetto UI version")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(levelname)s] %(message)s",
    )
    
    config = BuildConfig(
        perfetto_source_dir=Path(args.perfetto_source),
        storage_dir=Path(args.storage_dir),
        ui_version=args.ui_version,
    )
    
    builder = TraceProcessorBuilder(config)
    result = builder.build()
    
    print(json.dumps(result.to_dict(), indent=2))

