"""
Configuration file manager for symlink operations.

This module handles:
- Loading symlink manifests from JSON
- Detecting existing configurations
- Creating and verifying symlinks
- Backing up existing files
"""

import json
import sys
from pathlib import Path

from .helpers import get_home_dir, safe_symlink


class ConfigManager:
    """Manages dotfiles symlinks and configuration."""

    def __init__(self, repo_root: Path):
        """
        Initialize ConfigManager.

        Args:
            repo_root: Root directory of the dotfiles repository
        """
        self.repo_root = repo_root.resolve()
        self.home_dir = get_home_dir()
        self.manifest_path = self.repo_root / "manifests" / "links.json"

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")

    def load_manifest(self) -> dict[str, str]:
        """
        Load symlink manifest from JSON.

        Returns:
            Dictionary mapping repo paths to home paths
        """
        with open(self.manifest_path, "r") as f:
            return json.load(f)

    def detect_existing_configs(self) -> dict[str, Path]:
        """
        Detect existing configuration files that would be overwritten.

        Returns:
            Dictionary of config names to their paths
        """
        manifest = self.load_manifest()
        existing = {}

        for repo_path_str, home_path_str in manifest.items():
            # Expand ~ in path
            home_path = Path(home_path_str).expanduser()

            if home_path.exists():
                existing[repo_path_str] = home_path

        return existing

    def backup_existing_config(self, config_path: Path) -> bool:
        """
        Backup an existing configuration file.

        Args:
            config_path: Path to file to backup

        Returns:
            True if backup successful
        """
        if not config_path.exists():
            return True

        backup_path = config_path.with_suffix(config_path.suffix + ".backup")

        # Don't overwrite existing backups
        if backup_path.exists():
            return True

        try:
            if config_path.is_dir():
                import shutil

                shutil.copytree(config_path, backup_path)
            else:
                config_path.read_text()  # Verify readable
                backup_path.write_text(config_path.read_text())

            print(f"   ✓ Backed up: {config_path} → {backup_path}")
            return True
        except Exception as e:
            print(f"   ✗ Backup failed: {e}", file=sys.stderr)
            return False

    def symlink_configs(
        self,
        force: bool = False,
        verbose: bool = True,
        backup: bool = True,
    ) -> tuple[int, int]:
        """
        Create symlinks for all configurations in manifest.

        Args:
            force: Overwrite existing symlinks
            verbose: Print operations
            backup: Backup existing configs before overwriting

        Returns:
            Tuple of (successful_count, failed_count)
        """
        manifest = self.load_manifest()
        successful = 0
        failed = 0

        for repo_path_str, home_path_str in manifest.items():
            # Resolve paths
            source = self.repo_root / repo_path_str
            target = Path(home_path_str).expanduser()

            if not source.exists():
                if verbose:
                    print(f"✗ Source not found: {source}")
                failed += 1
                continue

            # Backup existing config if requested
            if backup and target.exists() and not target.is_symlink():
                self.backup_existing_config(target)

            # Create symlink
            if safe_symlink(source, target, force=force, verbose=verbose):
                successful += 1
            else:
                failed += 1

        return successful, failed

    def verify_symlinks(self) -> tuple[list[str], list[str]]:
        """
        Verify all symlinks are correctly set up.

        Returns:
            Tuple of (valid_links, broken_links)
        """
        manifest = self.load_manifest()
        valid = []
        broken = []

        for repo_path_str, home_path_str in manifest.items():
            source = self.repo_root / repo_path_str
            target = Path(home_path_str).expanduser()

            if not target.is_symlink():
                broken.append(str(target))
            elif target.resolve() != source.resolve():
                broken.append(str(target))
            else:
                valid.append(str(target))

        return valid, broken
