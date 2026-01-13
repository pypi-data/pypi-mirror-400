"""
SudoDog Exec Blocker - Python wrapper for LD_PRELOAD command blocking

This module compiles and manages the exec_blocker.so library that intercepts
dangerous commands before they execute.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List


class ExecBlocker:
    """Manages the LD_PRELOAD exec blocking library."""

    # Default location for the compiled library
    DEFAULT_LIB_DIR = Path.home() / ".sudodog" / "lib"
    LIB_NAME = "libexec_blocker.so"

    # Source file is bundled with the package
    SOURCE_FILE = "exec_blocker.c"

    def __init__(self, lib_dir: Optional[Path] = None):
        """Initialize the exec blocker.

        Args:
            lib_dir: Directory to store the compiled library.
                    Defaults to ~/.sudodog/lib/
        """
        self.lib_dir = Path(lib_dir) if lib_dir else self.DEFAULT_LIB_DIR
        self.lib_path = self.lib_dir / self.LIB_NAME
        self._source_path: Optional[Path] = None

    def _get_source_path(self) -> Path:
        """Get the path to the C source file."""
        if self._source_path:
            return self._source_path

        # Look for the source file relative to this module
        module_dir = Path(__file__).parent
        source_path = module_dir / self.SOURCE_FILE

        if source_path.exists():
            self._source_path = source_path
            return source_path

        raise FileNotFoundError(
            f"Could not find {self.SOURCE_FILE} in {module_dir}"
        )

    def is_compiled(self) -> bool:
        """Check if the library is already compiled."""
        return self.lib_path.exists()

    def needs_recompile(self) -> bool:
        """Check if the library needs to be recompiled."""
        if not self.is_compiled():
            return True

        try:
            source_path = self._get_source_path()
            source_mtime = source_path.stat().st_mtime
            lib_mtime = self.lib_path.stat().st_mtime
            return source_mtime > lib_mtime
        except FileNotFoundError:
            return True

    def compile(self, force: bool = False) -> bool:
        """Compile the exec blocker library.

        Args:
            force: Force recompilation even if library exists.

        Returns:
            True if compilation succeeded, False otherwise.
        """
        if not force and self.is_compiled() and not self.needs_recompile():
            return True

        # Check for GCC
        if not shutil.which("gcc"):
            print("Warning: GCC not found, cannot compile exec blocker")
            return False

        try:
            source_path = self._get_source_path()
        except FileNotFoundError as e:
            print(f"Warning: {e}")
            return False

        # Create library directory
        self.lib_dir.mkdir(parents=True, exist_ok=True)

        # Compile the library
        compile_cmd = [
            "gcc",
            "-shared",
            "-fPIC",
            "-O2",
            "-o", str(self.lib_path),
            str(source_path),
            "-ldl"
        ]

        try:
            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"Warning: Failed to compile exec blocker: {result.stderr}")
                return False

            # Make the library executable
            self.lib_path.chmod(0o755)
            return True

        except subprocess.TimeoutExpired:
            print("Warning: Compilation timed out")
            return False
        except Exception as e:
            print(f"Warning: Compilation failed: {e}")
            return False

    def get_env_vars(
        self,
        additional_patterns: Optional[List[str]] = None,
        log_path: Optional[Path] = None,
        debug: bool = False
    ) -> dict:
        """Get environment variables needed to enable the exec blocker.

        Args:
            additional_patterns: Extra patterns to block (semicolon-separated).
            log_path: Path to log blocked commands.
            debug: Enable debug output.

        Returns:
            Dictionary of environment variables to set.
        """
        if not self.is_compiled():
            if not self.compile():
                return {}

        env = {
            "LD_PRELOAD": str(self.lib_path)
        }

        if additional_patterns:
            env["SUDODOG_BLOCKED_PATTERNS"] = ";".join(additional_patterns)

        if log_path:
            env["SUDODOG_BLOCK_LOG"] = str(log_path)

        if debug:
            env["SUDODOG_EXEC_DEBUG"] = "1"

        return env

    def get_preload_path(self) -> Optional[str]:
        """Get the path to the compiled library for LD_PRELOAD.

        Returns:
            Path to the library, or None if not compiled.
        """
        if not self.is_compiled():
            if not self.compile():
                return None
        return str(self.lib_path)


# Global instance
_blocker: Optional[ExecBlocker] = None


def get_blocker() -> ExecBlocker:
    """Get the global ExecBlocker instance."""
    global _blocker
    if _blocker is None:
        _blocker = ExecBlocker()
    return _blocker


def setup_exec_blocking(
    env: dict,
    additional_patterns: Optional[List[str]] = None,
    log_path: Optional[Path] = None,
    debug: bool = False
) -> dict:
    """Set up exec blocking in the given environment dict.

    This modifies the environment dict in-place and also returns it.

    Args:
        env: Environment dictionary to modify.
        additional_patterns: Extra patterns to block.
        log_path: Path to log blocked commands.
        debug: Enable debug output.

    Returns:
        The modified environment dictionary.
    """
    blocker = get_blocker()
    blocking_env = blocker.get_env_vars(
        additional_patterns=additional_patterns,
        log_path=log_path,
        debug=debug
    )

    # Handle existing LD_PRELOAD
    if "LD_PRELOAD" in env and "LD_PRELOAD" in blocking_env:
        env["LD_PRELOAD"] = f"{blocking_env['LD_PRELOAD']}:{env['LD_PRELOAD']}"
        del blocking_env["LD_PRELOAD"]

    env.update(blocking_env)
    return env


def is_available() -> bool:
    """Check if exec blocking is available (GCC installed, etc.)."""
    if not shutil.which("gcc"):
        return False

    blocker = get_blocker()
    try:
        blocker._get_source_path()
        return True
    except FileNotFoundError:
        return False


def compile_if_needed() -> bool:
    """Compile the exec blocker if needed.

    Returns:
        True if the blocker is ready to use.
    """
    blocker = get_blocker()
    if blocker.is_compiled() and not blocker.needs_recompile():
        return True
    return blocker.compile()
