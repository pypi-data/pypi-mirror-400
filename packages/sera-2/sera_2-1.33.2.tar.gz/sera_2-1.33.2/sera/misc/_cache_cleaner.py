from __future__ import annotations

from pathlib import Path

from loguru import logger

from sera.misc._file_writer import SERA_CACHE_DIR


class CacheCleaner:
    """Cleans up stale cache files after code generation.

    After code generation, if a file is no longer being generated (e.g., the
    schema was modified and a class was removed), the cache file in `.sera/`
    should also be cleaned up.

    This class scans all `.sera` directories within the given root directory
    and removes cache files whose corresponding source files no longer exist.
    """

    def __init__(self, root_dir: Path):
        """Initialize the cache cleaner.

        Args:
            root_dir: The root directory of the generated application.
                      All `.sera` directories within this root will be scanned.
        """
        self.root_dir = root_dir

    def cleanup(self) -> int:
        """Remove cache files that no longer have corresponding source files.

        Returns:
            The number of stale cache files that were removed.
        """
        removed_count = 0

        # Find all .sera directories within the root
        for cache_dir in self.root_dir.rglob(SERA_CACHE_DIR):
            if not cache_dir.is_dir():
                raise ValueError(f"`{cache_dir}` is not a directory")

            # The parent of the cache dir (.sera) is the source directory
            source_dir = cache_dir.parent

            for cache_file in cache_dir.iterdir():
                if not cache_file.is_file():
                    raise ValueError(f"`{cache_file}` is not a file")

                # Get the corresponding source file path
                source_file = source_dir / cache_file.name

                if not source_file.exists():
                    logger.debug(
                        "Removing stale cache file `{}` (source file removed)",
                        cache_file,
                    )
                    cache_file.unlink()
                    removed_count += 1

            if sum(1 for _ in cache_dir.iterdir()) == 0:
                logger.debug(
                    "Removing empty cache directory `{}`",
                    cache_dir,
                )
                cache_dir.rmdir()

        if removed_count > 0:
            logger.info("Removed {} stale cache file(s)", removed_count)

        return removed_count
