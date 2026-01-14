"""Validation mixin for OHLCV data."""

from __future__ import annotations

from datetime import datetime

import polars as pl
import structlog

from ml4t.data.core.exceptions import DataValidationError

logger = structlog.get_logger()


class ValidationMixin:
    """Mixin providing OHLCV data validation.

    Validates that data conforms to the canonical OHLCV schema
    and enforces OHLC invariants (high >= low, etc.).

    Example:
        class MyProvider(ValidationMixin):
            def fetch_data(self, symbol):
                data = self._do_fetch(symbol)
                return self._validate_ohlcv(data, "my_provider")
    """

    # Required columns for OHLCV data
    REQUIRED_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]

    def _validate_inputs(
        self,
        symbol: str,
        start: str,
        end: str,
        frequency: str,  # noqa: ARG002
    ) -> None:
        """Validate input parameters.

        Args:
            symbol: Symbol to fetch
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            frequency: Data frequency

        Raises:
            ValueError: If inputs are invalid
        """
        if not symbol or not symbol.strip():
            raise ValueError("Symbol cannot be empty")

        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format (expected YYYY-MM-DD): {e}") from e

        if start_dt > end_dt:
            raise ValueError("Start date must be before or equal to end date")

    def _validate_ohlcv(
        self,
        df: pl.DataFrame,
        provider_name: str,
    ) -> pl.DataFrame:
        """Validate and normalize OHLCV data.

        Args:
            df: DataFrame to validate
            provider_name: Provider name for error messages

        Returns:
            Validated and normalized DataFrame

        Raises:
            DataValidationError: If validation fails
        """
        # Handle empty responses
        if df.is_empty():
            logger.debug("Empty DataFrame received - no data for range")
            return df

        # Check required columns
        missing = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            raise DataValidationError(provider_name, f"Missing required columns: {missing}")

        # Validate OHLC invariants
        self._validate_ohlc_invariants(df, provider_name)

        # Sort and deduplicate
        df = df.sort("timestamp").unique(subset=["timestamp"], maintain_order=True)

        return df

    def _validate_ohlc_invariants(
        self,
        df: pl.DataFrame,
        provider_name: str,
    ) -> None:
        """Validate OHLC price invariants.

        Checks:
            - high >= low
            - high >= open
            - high >= close
            - low <= open
            - low <= close

        Args:
            df: DataFrame to validate
            provider_name: Provider name for error messages

        Raises:
            DataValidationError: If invariants violated
        """
        invalid_ohlc = (
            (df["high"] < df["low"])
            | (df["high"] < df["open"])
            | (df["high"] < df["close"])
            | (df["low"] > df["open"])
            | (df["low"] > df["close"])
        )

        if invalid_ohlc.any():
            n_invalid = invalid_ohlc.sum()
            raise DataValidationError(
                provider_name, f"Found {n_invalid} rows with invalid OHLC relationships"
            )

    def _validate_no_nulls(
        self,
        df: pl.DataFrame,
        provider_name: str,
        columns: list[str] | None = None,
    ) -> None:
        """Validate no null values in specified columns.

        Args:
            df: DataFrame to validate
            provider_name: Provider name for error messages
            columns: Columns to check (default: all required columns)

        Raises:
            DataValidationError: If nulls found
        """
        check_columns = columns or self.REQUIRED_COLUMNS

        for col in check_columns:
            if col in df.columns:
                null_count = df[col].null_count()
                if null_count > 0:
                    raise DataValidationError(
                        provider_name,
                        f"Column '{col}' contains {null_count} null values",
                    )

    def _validate_positive_values(
        self,
        df: pl.DataFrame,
        provider_name: str,
    ) -> None:
        """Validate prices and volume are positive.

        Args:
            df: DataFrame to validate
            provider_name: Provider name for error messages

        Raises:
            DataValidationError: If negative values found
        """
        numeric_cols = ["open", "high", "low", "close", "volume"]

        for col in numeric_cols:
            if col in df.columns:
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    raise DataValidationError(
                        provider_name,
                        f"Column '{col}' contains {negative_count} negative values",
                    )
