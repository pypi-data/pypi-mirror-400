"""Flat file storage implementation.

Simple storage backend that stores each key as a single parquet file.
Suitable for smaller datasets or when partitioning is not beneficial.
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import polars as pl
from filelock import FileLock

from .backend import StorageBackend, StorageConfig


class FlatStorage(StorageBackend):
    """Flat file storage without partitioning.

    This implementation provides:
    - Simple single-file storage per key
    - Atomic writes with temp file pattern
    - Metadata tracking in JSON manifests
    - File locking for concurrent access safety
    - Polars lazy evaluation throughout
    """

    def __init__(self, config: StorageConfig):
        """Initialize flat storage backend.

        Args:
            config: Storage configuration
        """
        super().__init__(config)
        self.metadata_dir = self.base_path / ".metadata"
        self.metadata_dir.mkdir(exist_ok=True)

    def write(
        self, data: pl.LazyFrame | pl.DataFrame, key: str, metadata: dict[str, Any] | None = None
    ) -> Path:
        """Write data as a single file.

        Args:
            data: Data to write
            key: Storage key (e.g., "BTC-USD")
            metadata: Optional metadata

        Returns:
            Path to written file
        """
        # Ensure LazyFrame for efficiency
        lazy_data = self._ensure_lazy(data)

        # Create file path
        file_path = self.base_path / f"{key.replace('/', '_')}.parquet"

        # Collect and write atomically
        df = lazy_data.collect()
        self._atomic_write(df, file_path)

        # Update metadata
        if self.config.metadata_tracking:
            self._update_metadata(
                key,
                {
                    "last_updated": datetime.now().isoformat(),
                    "file_path": str(file_path.relative_to(self.base_path)),
                    "row_count": len(df),
                    "schema": list(df.columns),
                    "file_size_mb": file_path.stat().st_size / (1024 * 1024),
                    "custom": metadata or {},
                },
            )

        return file_path

    def read(
        self,
        key: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        columns: list[str] | None = None,
    ) -> pl.LazyFrame:
        """Read data from flat file.

        Args:
            key: Storage key
            start_date: Optional start date filter
            end_date: Optional end date filter
            columns: Optional columns to select

        Returns:
            LazyFrame with requested data
        """
        file_path = self.base_path / f"{key.replace('/', '_')}.parquet"

        if not file_path.exists():
            raise KeyError(f"Key '{key}' not found in storage")

        # Use lazy reading
        lf = pl.scan_parquet(file_path)

        # Apply column selection
        if columns:
            lf = lf.select(columns)

        # Apply date filters if timestamp column exists
        schema = lf.schema
        if "timestamp" in schema:
            if start_date:
                lf = lf.filter(pl.col("timestamp") >= start_date)
            if end_date:
                lf = lf.filter(pl.col("timestamp") < end_date)

        return lf

    def list_keys(self) -> list[str]:
        """List all keys in storage.

        Returns:
            List of storage keys
        """
        keys = []
        for path in self.base_path.glob("*.parquet"):
            # Convert from filesystem-safe name
            key = path.stem.replace("_", "/")
            keys.append(key)
        return sorted(keys)

    def exists(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: Storage key

        Returns:
            True if key exists
        """
        file_path = self.base_path / f"{key.replace('/', '_')}.parquet"
        return file_path.exists()

    def delete(self, key: str) -> bool:
        """Delete data for a key.

        Args:
            key: Storage key

        Returns:
            True if successful
        """
        file_path = self.base_path / f"{key.replace('/', '_')}.parquet"
        if file_path.exists():
            file_path.unlink()

            # Remove metadata
            metadata_file = self.metadata_dir / f"{key.replace('/', '_')}.json"
            if metadata_file.exists():
                metadata_file.unlink()

            return True
        return False

    def get_metadata(self, key: str) -> dict[str, Any] | None:
        """Get metadata for a key.

        Args:
            key: Storage key

        Returns:
            Metadata dict or None
        """
        metadata_file = self.metadata_dir / f"{key.replace('/', '_')}.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                return json.load(f)
        return None

    def _atomic_write(self, df: pl.DataFrame, target_path: Path) -> None:
        """Write DataFrame atomically using temp file pattern.

        Args:
            df: DataFrame to write
            target_path: Target file path
        """
        # Write to temp file first
        with tempfile.NamedTemporaryFile(
            dir=target_path.parent, suffix=".parquet.tmp", delete=False
        ) as tmp_file:
            tmp_path = Path(tmp_file.name)

            # Write with compression
            df.write_parquet(tmp_path, compression=self.config.compression or "zstd")

            # Atomic rename
            tmp_path.replace(target_path)

    def _update_metadata(self, key: str, metadata: dict[str, Any]) -> None:
        """Update metadata for a key.

        Args:
            key: Storage key
            metadata: Metadata to store
        """
        metadata_file = self.metadata_dir / f"{key.replace('/', '_')}.json"

        if self.config.enable_locking:
            lock_file = self.metadata_dir / f"{key.replace('/', '_')}.lock"
            lock = FileLock(lock_file, timeout=10)

            with lock:
                self._write_metadata_file(metadata_file, metadata)
        else:
            self._write_metadata_file(metadata_file, metadata)

    def _write_metadata_file(self, path: Path, metadata: dict[str, Any]) -> None:
        """Write metadata to file.

        Args:
            path: Metadata file path
            metadata: Metadata to write
        """
        with tempfile.NamedTemporaryFile(
            dir=path.parent, mode="w", suffix=".json.tmp", delete=False
        ) as tmp_file:
            json.dump(metadata, tmp_file, indent=2, default=str)
            tmp_path = Path(tmp_file.name)
            tmp_path.replace(path)
