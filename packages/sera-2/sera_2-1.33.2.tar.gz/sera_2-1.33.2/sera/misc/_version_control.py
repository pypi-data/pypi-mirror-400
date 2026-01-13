"""Version control safety checks for code generation."""

from __future__ import annotations

import subprocess
from pathlib import Path

from loguru import logger


class VersionControlError(Exception):
    """Raised when version control safety check fails."""

    pass


def is_git_repository(path: Path) -> bool:
    """
    Check if the given path is within a Git repository.

    Args:
        path: The path to check.

    Returns:
        True if the path is within a Git repository, False otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=path,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except FileNotFoundError:
        # Git is not installed
        return False


def has_uncommitted_changes(path: Path) -> bool:
    """
    Check if the Git repository has uncommitted changes (staged or unstaged).

    Args:
        path: A path within the Git repository to check.

    Returns:
        True if there are uncommitted changes, False otherwise.

    Raises:
        VersionControlError: If the path is not within a Git repository.
    """
    if not is_git_repository(path):
        raise VersionControlError(f"'{path}' is not within a Git repository")

    # Check for both staged and unstaged changes
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=path,
        capture_output=True,
        text=True,
        check=True,
    )
    return len(result.stdout.strip()) > 0


def check_clean_repo_or_token(
    repo_path: Path,
    session_token: str | None = None,
    allow_dirty_repo: bool = False,
) -> None:
    """
    Ensure the repo is clean for code generation.

    This function performs version control safety checks before code generation.
    If allow_dirty_repo is True, all checks are skipped.

    If session_token is provided:
      - If the token file exists, skip the check (allows parallel runs)
      - If the token file doesn't exist, perform the check and create the token file

    Args:
        repo_path: The path to the repository to check.
        session_token: Optional path to a token file for parallel runs.
        allow_dirty_repo: If True, skip all version control checks.

    Raises:
        VersionControlError: If the repo is not a Git repo or has uncommitted changes.
    """
    if allow_dirty_repo:
        logger.debug("Skipping version control checks (allow_dirty_repo=True)")
        return

    # Check if session token exists (parallel run case)
    if session_token is not None:
        token_path = Path(session_token)
        if token_path.exists():
            logger.debug(
                "Session token '{}' exists, skipping version control checks",
                session_token,
            )
            return

    # Perform version control checks
    if not is_git_repository(repo_path):
        raise VersionControlError(
            f"'{repo_path}' is not within a Git repository. "
            "Code generation requires a version-controlled repository. "
            "Use --allow-dirty-repo to skip this check."
        )

    if has_uncommitted_changes(repo_path):
        raise VersionControlError(
            f"'{repo_path}' has uncommitted changes. "
            "Please commit or stash your changes before running code generation. "
            "Use --allow-dirty-repo to skip this check."
        )

    logger.info("Version control check passed: repository is clean")

    # Create session token if provided (for parallel runs)
    if session_token is not None:
        token_path = Path(session_token)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.touch()
        logger.debug("Created session token '{}'", session_token)


def read_from_git_head(file_path: Path) -> str | None:
    """Read file content from Git HEAD (latest commit).

    This ensures idempotent operations by always comparing against
    the committed version, not the working directory version.

    Args:
        file_path: Path to the file to read from Git HEAD (can be absolute or relative).

    Returns:
        File content from HEAD, or None if file is not tracked by Git
        or doesn't exist in HEAD.
    """
    # Get the git repository root
    repo_root_result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        cwd=file_path.parent,
        check=True,
    )
    repo_root = Path(repo_root_result.stdout.strip())

    # Make file_path relative to repo root
    abs_file_path = file_path.resolve()
    relative_path = abs_file_path.relative_to(repo_root)

    try:
        # Get file content from HEAD
        result = subprocess.run(
            ["git", "show", f"HEAD:{relative_path}"],
            capture_output=True,
            text=True,
            cwd=repo_root,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError:
        # File not in Git, doesn't exist in HEAD, or path not relative to repo
        return None
