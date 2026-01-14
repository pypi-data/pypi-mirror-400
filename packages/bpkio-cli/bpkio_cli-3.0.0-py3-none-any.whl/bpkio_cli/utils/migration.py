"""
Migration utilities for bpkio-cli.

Handles migration of .bpkio directory from old locations to new locations,
particularly for Windows/WSL compatibility.
"""

import os
import shutil
from pathlib import Path

from loguru import logger

from bpkio_cli.core.paths import get_bpkio_home


def migrate_bpkio_directory():
    """
    Migrate .bpkio directory from old location (os.path.expanduser("~"))
    to new location in bic v3 (Path.home()) if they differ and old location has files.

    This handles the case where Windows/WSL might resolve ~ differently than Path.home(),
    or where a literal '~' directory was created.
    """
    old_home_expanded = Path(os.path.expanduser("~"))
    new_home = Path.home()

    # Also check for a literal '~' directory (Windows edge case)
    literal_tilde_dir = new_home / "~"

    logger.debug(
        f"Migration check: old_home_expanded={old_home_expanded}, "
        f"new_home={new_home}, literal_tilde={literal_tilde_dir}"
    )

    # Check multiple possible old locations
    possible_old_locations = []

    # 1. Check if expanded ~ differs from Path.home()
    if old_home_expanded.resolve() != new_home.resolve():
        possible_old_locations.append(old_home_expanded / ".bpkio")
        logger.debug(f"Found different expanded home: {old_home_expanded}")

    # 2. Check for literal ~ directory (Windows edge case)
    if literal_tilde_dir.exists() and literal_tilde_dir.is_dir():
        possible_old_locations.append(literal_tilde_dir / ".bpkio")
        logger.debug(f"Found literal ~ directory: {literal_tilde_dir}")

    # If they resolve to the same path and no literal ~, no migration needed
    if not possible_old_locations:
        logger.debug("No migration needed - paths are identical")
        return

    new_bpkio = get_bpkio_home()

    # Find the first old location that actually exists with files
    old_bpkio = None
    for possible_location in possible_old_locations:
        if possible_location.exists() and possible_location.is_dir():
            # Check if it has any of the files we care about
            if any(
                (possible_location / item).exists() for item in ["cli.cfg", "tenants"]
            ):
                old_bpkio = possible_location
                logger.debug(f"Found old .bpkio directory to migrate: {old_bpkio}")
                break

    # If no old directory found, nothing to migrate
    if old_bpkio is None:
        logger.debug("No old .bpkio directory found with files to migrate")
        return

    # Files/directories to migrate (in priority order)
    items_to_migrate = [
        "cli.cfg",  # Config file
        "tenants",  # Tenant profiles
    ]

    migrated_items = []

    try:
        # Ensure new directory exists
        new_bpkio.mkdir(parents=True, exist_ok=True)

        # Migrate each item if it exists and doesn't already exist in new location
        for item_name in items_to_migrate:
            old_item = old_bpkio / item_name
            new_item = new_bpkio / item_name

            # Skip if item doesn't exist in old location
            if not old_item.exists():
                continue

            # Skip if item already exists in new location (don't overwrite)
            if new_item.exists():
                logger.debug(f"Skipping {item_name} - already exists at {new_item}")
                continue

            if old_item.is_file():
                # Copy file
                shutil.copy2(old_item, new_item)
                migrated_items.append(item_name)
                logger.info(f"Migrated {item_name} from {old_item} to {new_item}")
            elif old_item.is_dir():
                # Copy directory recursively
                shutil.copytree(old_item, new_item, dirs_exist_ok=True)
                migrated_items.append(item_name)
                logger.info(
                    f"Migrated {item_name}/ directory from {old_item} to {new_item}"
                )

        if migrated_items:
            logger.info(
                f"Successfully migrated .bpkio directory from {old_bpkio} to {new_bpkio}. "
                f"Migrated items: {', '.join(migrated_items)}"
            )
            # Delete the old directory after successful migration
            try:
                if old_bpkio.exists():
                    shutil.rmtree(old_bpkio)
                    logger.info(f"Deleted old .bpkio directory at {old_bpkio}")

                    # Also try to delete the parent literal ~ directory if it's empty
                    parent_dir = old_bpkio.parent
                    if parent_dir.name == "~" and parent_dir.exists():
                        try:
                            # Only delete if empty (no other files/dirs)
                            if not any(parent_dir.iterdir()):
                                parent_dir.rmdir()
                                logger.info(
                                    f"Deleted empty literal ~ directory at {parent_dir}"
                                )
                        except Exception:
                            # Ignore errors deleting parent - it might have other files
                            pass
            except Exception as delete_error:
                logger.warning(
                    f"Failed to delete old .bpkio directory at {old_bpkio}: {delete_error}. "
                    "You may need to delete it manually."
                )
        else:
            logger.debug(f"No items found to migrate from {old_bpkio}")

    except Exception as e:
        logger.warning(
            f"Failed to migrate .bpkio directory from {old_bpkio} to {new_bpkio}: {e}"
        )
        # Don't raise - allow the application to continue with new location
