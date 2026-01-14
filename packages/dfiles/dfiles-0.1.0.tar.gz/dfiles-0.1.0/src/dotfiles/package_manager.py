"""
Package manager abstraction for macOS (Homebrew) and Windows (winget).
"""

import sys
from pathlib import Path

from .helpers import command_exists, get_platform, run_command


class PackageManager:
    """Handles package installation and updates across platforms."""

    def __init__(self, dry_run: bool = False, verbose: bool = True):
        """
        Initialize PackageManager.

        Args:
            dry_run: Whether to simulate commands without executing
            verbose: Whether to print operations
        """
        self.platform = get_platform()
        self.dry_run = dry_run
        self.verbose = verbose

    def install_packages(self, packages: list[str]) -> bool:
        """
        Install a list of packages.

        Args:
            packages: List of package names

        Returns:
            True if all packages installed successfully
        """
        if not packages:
            return True

        if self.platform == "macos":
            return self._brew_install(packages)
        elif self.platform == "windows":
            return self._winget_install(packages)
        elif self.platform == "linux":
            return self._apt_install(packages)
        else:
            print(f"✗ Unsupported platform: {self.platform}", file=sys.stderr)
            return False

    def update_packages(self) -> bool:
        """
        Update all packages on the system.

        Returns:
            True if update successful
        """
        if self.platform == "macos":
            return self._brew_update()
        elif self.platform == "windows":
            return self._winget_upgrade()
        elif self.platform == "linux":
            return self._apt_update()
        else:
            print(f"✗ Unsupported platform: {self.platform}", file=sys.stderr)
            return False

    def cleanup(self) -> bool:
        """
        Clean up package manager cache and unused packages.

        Returns:
            True if cleanup successful
        """
        if self.platform == "macos":
            return self._brew_cleanup()
        elif self.platform == "windows":
            # Windows doesn't have native cleanup
            return True
        elif self.platform == "linux":
            return self._apt_cleanup()
        else:
            return False

    # ==================== macOS / Homebrew ====================

    def _brew_install(self, packages: list[str]) -> bool:
        """Install packages via Homebrew."""
        if not command_exists("brew"):
            print(
                "✗ Homebrew not found. Please install Homebrew first.", file=sys.stderr
            )
            return False

        try:
            run_command(
                ["brew", "install"] + packages,
                verbose=self.verbose,
                dry_run=self.dry_run,
            )
            return True
        except Exception as e:
            print(f"✗ Homebrew install failed: {e}", file=sys.stderr)
            return False

    def _brew_update(self) -> bool:
        """Update Homebrew and all packages."""
        if not command_exists("brew"):
            print("✗ Homebrew not found.", file=sys.stderr)
            return False

        try:
            run_command(
                ["brew", "update"],
                verbose=self.verbose,
                dry_run=self.dry_run,
            )
            run_command(
                ["brew", "upgrade"],
                verbose=self.verbose,
                dry_run=self.dry_run,
            )
            return True
        except Exception as e:
            print(f"✗ Homebrew update failed: {e}", file=sys.stderr)
            return False

    def _brew_cleanup(self) -> bool:
        """Clean up Homebrew cache and unused packages."""
        if not command_exists("brew"):
            return False

        try:
            run_command(
                ["brew", "cleanup"],
                verbose=self.verbose,
                dry_run=self.dry_run,
            )
            run_command(
                ["brew", "autoremove"],
                verbose=self.verbose,
                dry_run=self.dry_run,
            )
            return True
        except Exception:
            return False

    def install_brewfile(self, brewfile_path: Path | None = None) -> bool:
        """
        Install packages from a Brewfile.

        Args:
            brewfile_path: Path to Brewfile (default: repo_root/Brewfile)

        Returns:
            True if successful
        """
        if not command_exists("brew"):
            print("✗ Homebrew not found.", file=sys.stderr)
            return False

        if brewfile_path is None:
            # Try to find Brewfile in current repo
            brewfile_path = Path.cwd() / "Brewfile"

        if not brewfile_path.exists():
            print(f"✗ Brewfile not found: {brewfile_path}", file=sys.stderr)
            return False

        try:
            run_command(
                ["brew", "bundle", "install", f"--file={brewfile_path}"],
                verbose=self.verbose,
                dry_run=self.dry_run,
            )
            return True
        except Exception as e:
            print(f"✗ Brewfile install failed: {e}", file=sys.stderr)
            return False

    # ==================== Windows / winget ====================

    def _winget_install(self, packages: list[str]) -> bool:
        """Install packages via winget."""
        if not command_exists("winget"):
            print(
                "✗ winget not found. Please install Windows Package Manager.",
                file=sys.stderr,
            )
            return False

        try:
            for package in packages:
                run_command(
                    ["winget", "install", "-e", "--id", package],
                    verbose=self.verbose,
                    dry_run=self.dry_run,
                )
            return True
        except Exception as e:
            print(f"✗ winget install failed: {e}", file=sys.stderr)
            return False

    def _winget_upgrade(self) -> bool:
        """Upgrade all packages via winget."""
        if not command_exists("winget"):
            print("✗ winget not found.", file=sys.stderr)
            return False

        try:
            run_command(
                ["winget", "upgrade", "--all"],
                verbose=self.verbose,
                dry_run=self.dry_run,
            )
            return True
        except Exception as e:
            print(f"✗ winget upgrade failed: {e}", file=sys.stderr)
            return False

    # ==================== Linux / apt ====================

    def _apt_install(self, packages: list[str]) -> bool:
        """Install packages via apt."""
        if not command_exists("apt-get"):
            print(
                "✗ apt-get not found. This system doesn't appear to use apt.",
                file=sys.stderr,
            )
            return False

        try:
            run_command(
                ["sudo", "apt-get", "install", "-y"] + packages,
                verbose=self.verbose,
                dry_run=self.dry_run,
            )
            return True
        except Exception as e:
            print(f"✗ apt install failed: {e}", file=sys.stderr)
            return False

    def _apt_update(self) -> bool:
        """Update apt packages."""
        if not command_exists("apt-get"):
            print("✗ apt-get not found.", file=sys.stderr)
            return False

        try:
            run_command(
                ["sudo", "apt-get", "update"],
                verbose=self.verbose,
                dry_run=self.dry_run,
            )
            run_command(
                ["sudo", "apt-get", "upgrade", "-y"],
                verbose=self.verbose,
                dry_run=self.dry_run,
            )
            return True
        except Exception as e:
            print(f"✗ apt update failed: {e}", file=sys.stderr)
            return False

    def _apt_cleanup(self) -> bool:
        """Clean up apt cache."""
        if not command_exists("apt-get"):
            return False

        try:
            run_command(
                ["sudo", "apt-get", "autoremove", "-y"],
                verbose=self.verbose,
                dry_run=self.dry_run,
            )
            run_command(
                ["sudo", "apt-get", "clean"],
                verbose=self.verbose,
                dry_run=self.dry_run,
            )
            return True
        except Exception:
            return False
