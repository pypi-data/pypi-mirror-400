from __future__ import annotations

import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import black
import black.mode
import isort
from loguru import logger
from tqdm import tqdm

from sera.misc._version_control import read_from_git_head
from sera.typing import Language

# Name of the cache directory for storing previously generated files
SERA_CACHE_DIR = ".sera"


@dataclass
class WriteJob:
    """Represents a pending file write operation."""

    outfile: Path
    content: str  # Unformatted content (includes copyright)
    language: Language
    first_party_packages: list[str] = field(default_factory=list)  # For isort


class FileWriter:
    """Singleton class responsible for deferred file writing with 3-way merge.

    This class collects all file write operations during code generation and
    processes them at the end. This allows:
    1. Parallel formatting of all TypeScript files
    2. Proper diff generation after formatting
    3. Idempotent rebase-style merging when user has modified generated files

    The class maintains a cache in `.sera/` directory to track previously
    generated content. When user has modified a file, it performs a 3-way
    merge to apply the new generated code while preserving user changes.
    """

    instance: FileWriter | None = None

    def __init__(self):
        self.pending_jobs: list[WriteJob] = []

    @staticmethod
    def get_instance() -> FileWriter:
        if FileWriter.instance is None:
            FileWriter.instance = FileWriter()
        return FileWriter.instance

    @staticmethod
    def reset_instance() -> None:
        """Reset the singleton instance. Useful for testing."""
        FileWriter.instance = None

    def register(self, job: WriteJob) -> None:
        """Register a write job for later execution."""
        self.pending_jobs.append(job)

    def process(self, parallel: bool = True) -> None:
        """Process all pending write jobs.

        For each job:
        1. Format the content (Python with black/isort, TypeScript with prettier)
        2. Check if file exists and compare with cached previous generation
        3. If user has modified the file, perform 3-way merge (rebase)
        4. If file matches cache or doesn't exist, write new content directly
        5. Update cache with new generated content
        """
        if len(self.pending_jobs) == 0:
            return

        # First, format all files
        formatted_jobs = self._format_all_jobs()

        # Then, process each job in parallel (git commands can be slow)
        def process_job_wrapper(args: tuple[WriteJob, str]) -> None:
            job, formatted_content = args
            self._process_job(job, formatted_content)

        if parallel:
            with ThreadPoolExecutor() as executor:
                list(
                    tqdm(
                        executor.map(process_job_wrapper, formatted_jobs),
                        desc="Writing files",
                        total=len(formatted_jobs),
                    )
                )
        else:
            for args in tqdm(formatted_jobs, desc="Writing files"):
                process_job_wrapper(args)

        self.pending_jobs.clear()

    def _get_cache_path(self, outfile: Path) -> Path:
        """Get the cache file path for a given output file.

        Cache files are stored in `.sera/` directory relative to the output file's
        parent directory, preserving the filename.

        Example:
            outfile: /project/src/models/user.py
            cache:   /project/src/models/.sera/user.py
        """
        return outfile.parent / SERA_CACHE_DIR / outfile.name

    def _read_cache(self, outfile: Path) -> str | None:
        """Read the cached content for a file, if it exists."""
        cache_path = self._get_cache_path(outfile)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        return read_from_git_head(cache_path)

    def _write_cache(self, outfile: Path, content: str) -> None:
        """Write content to the cache for a file."""
        cache_path = self._get_cache_path(outfile)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(content)

    def _format_all_jobs(self) -> list[tuple[WriteJob, str]]:
        """Format all jobs, returning (job, formatted_content) pairs."""
        results: list[tuple[WriteJob, str]] = []

        # Separate Python and TypeScript jobs
        python_jobs = [j for j in self.pending_jobs if j.language == Language.Python]
        ts_jobs = [j for j in self.pending_jobs if j.language == Language.Typescript]

        # Format Python jobs (fast, can be done inline)
        for job in python_jobs:
            try:
                formatted = self._format_python(job.content, job.first_party_packages)
                results.append((job, formatted))
            except Exception:
                logger.error("Error formatting Python file {}", job.outfile)
                print(">>> Content")
                print(job.content)
                print("<<<")
                raise

        # Format TypeScript jobs in parallel (slow, uses subprocess)
        if len(ts_jobs) > 0:
            with ThreadPoolExecutor() as executor:
                ts_results = list(
                    tqdm(
                        executor.map(
                            lambda j: (j, self._format_typescript(j)),
                            ts_jobs,
                        ),
                        total=len(ts_jobs),
                        desc="Formatting TypeScript files",
                    )
                )
                for job, formatted in ts_results:
                    results.append((job, formatted))

        return results

    def _format_python(self, content: str, first_party_packages: list[str]) -> str:
        """Format Python code using black and isort."""
        code = black.format_str(
            content,
            mode=black.Mode(
                target_versions={black.mode.TargetVersion.PY312},
            ),
        )
        code = isort.code(code, profile="black", known_first_party=first_party_packages)
        return code

    def _format_typescript(self, job: WriteJob) -> str:
        """Format TypeScript code using prettier.

        We need to write to a temp file because prettier works on files.
        """
        # Write content to the target file temporarily for prettier
        job.outfile.parent.mkdir(parents=True, exist_ok=True)

        # Write content (already includes copyright from Module)
        job.outfile.write_text(job.content)

        try:
            subprocess.check_output(
                ["npx", "prettier", "--write", str(job.outfile.absolute())],
                cwd=job.outfile.parent,
                stderr=subprocess.STDOUT,
            )
            return job.outfile.read_text()
        except subprocess.CalledProcessError as e:
            logger.error("Error formatting TypeScript file {}: {}", job.outfile, e)
            raise

    def _three_way_merge(self, base: str, ours: str, theirs: str) -> tuple[str, bool]:
        """Perform 3-way merge using git merge-file.

        This implements a rebase-style merge where:
        - base (v0): old generated code (common ancestor)
        - ours (v2): new generated code (what we want to apply)
        - theirs (v1): user's current version (with their modifications)

        The merge order is: base -> ours -> theirs
        This means we apply the new generation, then replay user changes on top.

        Args:
            base: v0 - old generated code from cache
            ours: v2 - new generated code
            theirs: v1 - user's current version

        Returns:
            Tuple of (merged_content, has_conflicts)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            base_file = tmpdir / "base"
            ours_file = tmpdir / "ours"
            theirs_file = tmpdir / "theirs"

            base_file.write_text(base)
            ours_file.write_text(ours)
            theirs_file.write_text(theirs)

            # git merge-file modifies the "ours" file in place
            # Exit code: 0 = clean merge, >0 = number of conflicts
            try:
                subprocess.run(
                    [
                        "git",
                        "merge-file",
                        "-L",
                        "GENERATED (sera output)",
                        "-L",
                        "BASE (previous sera output)",
                        "-L",
                        "CURRENT (your version)",
                        str(ours_file),
                        str(base_file),
                        str(theirs_file),
                    ],
                    check=True,
                    capture_output=True,
                )
                # Clean merge
                return ours_file.read_text(), False
            except subprocess.CalledProcessError as e:
                # Conflicts occurred (exit code > 0), but file still contains merged result
                if e.returncode > 0:
                    return ours_file.read_text(), True
                raise

    def _process_job(self, job: WriteJob, formatted_content: str) -> None:
        """Process a single write job after formatting.

        Logic:
        1. If file doesn't exist -> write new file and update cache
        2. If file exists:
           a. Read cached previous generation (v0)
           b. If no cache exists -> first generation, just overwrite and cache
           c. If current file matches cache -> user hasn't modified, overwrite
           d. If current file differs from cache -> user modified, 3-way merge

        Always update cache with new generated content at the end.
        """
        cached_content = self._read_cache(job.outfile)  # v0

        if not job.outfile.exists():
            # New file - just write it and cache
            job.outfile.parent.mkdir(parents=True, exist_ok=True)
            job.outfile.write_text(formatted_content)
            self._write_cache(job.outfile, formatted_content)
            return

        # Read current content from Git HEAD for idempotency
        current_content = read_from_git_head(job.outfile)  # v1
        if current_content is None:
            # File not in Git, but we got to this path because we rerun the command
            # It means users haven't modified the file, so we can just overwrite it and cache
            job.outfile.write_text(formatted_content)
            self._write_cache(job.outfile, formatted_content)
            return

        # Check if content is the same as what we're about to write
        if current_content == formatted_content:
            logger.debug("File {} is unchanged, skipping", job.outfile)
            # Still update cache in case it was missing
            self._write_cache(job.outfile, formatted_content)
            return

        # Content differs - check if user has modified the file
        if cached_content is None:
            # No cache exists - we may have missed not caching the generated content
            # The safest way is to write the cache with the latest generation and
            # user can manually resolve any conflicts later
            logger.info(
                "No cache for `{}`, writing the latest generation.",
                job.outfile,
            )
            cached_content = formatted_content

        if current_content == cached_content:
            # File matches cache - user hasn't modified it, safe to overwrite
            logger.debug("File {} matches cache, overwriting", job.outfile)
            job.outfile.write_text(formatted_content)
            self._write_cache(job.outfile, formatted_content)
            return

        # User has modified the file - perform 3-way merge
        # base=v0 (cached), ours=v2 (new generated), theirs=v1 (current user version)
        merged_content, has_conflicts = self._three_way_merge(
            base=cached_content,
            ours=formatted_content,
            theirs=current_content,
        )

        job.outfile.write_text(merged_content)
        self._write_cache(job.outfile, formatted_content)

        if has_conflicts:
            logger.warning(
                "Merge conflicts in `{}`. Please resolve manually.",
                job.outfile,
            )
        else:
            logger.info(
                "Merged user modifications with new generated code in `{}`.",
                job.outfile,
            )
