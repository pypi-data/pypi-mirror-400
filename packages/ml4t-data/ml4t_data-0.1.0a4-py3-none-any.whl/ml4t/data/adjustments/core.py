"""Core corporate actions adjustment functions.

This module implements price adjustment algorithms for stock splits and
dividends, following the industry-standard methodology used by Quandl, Yahoo
Finance, and other major data providers.

The adjustment works BACKWARD from the most recent date, using this formula:
    Adj[i] = Adj[i+1] + Adj[i+1] × ((Price[i] × Split[i+1] - Price[i+1] - Div[i+1]) / Price[i+1])

Where indices go from newest (0) to oldest (n).
"""

import polars as pl


def apply_corporate_actions(
    prices: pl.DataFrame,
    split_col: str = "split_ratio",
    dividend_col: str = "ex-dividend",
    price_cols: list[str] | None = None,
    volume_col: str | None = "volume",
) -> pl.DataFrame:
    """Apply both split and dividend adjustments to create fully adjusted prices.

    Uses the industry-standard backward-adjustment methodology where each day's
    adjusted price is calculated from the next day's adjusted price and corporate
    actions. This matches the approach used by Quandl, Yahoo Finance, and other
    major data providers.

    Args:
        prices: DataFrame with date-sorted prices and corporate action data
        split_col: Column with split ratios (default: 'split_ratio')
        dividend_col: Column with dividend amounts (default: 'ex-dividend')
        price_cols: Price columns to adjust (default: ['open', 'high', 'low', 'close'])
        volume_col: Volume column to adjust (default: 'volume')

    Returns:
        DataFrame with fully adjusted prices (splits + dividends)

    Formula:
        For each price column, working backwards from newest to oldest:
        Adj[i] = Adj[i+1] + Adj[i+1] × ((Price[i] × Split[i+1] - Price[i+1] - Div[i+1]) / Price[i+1])

        Simplified:
        Adj[i] = Adj[i+1] × (Price[i] × Split[i+1] - Div[i+1]) / Price[i+1]

    Example:
        >>> # Validate against Quandl's pre-calculated adjusted prices
        >>> result = apply_corporate_actions(quandl_df)
        >>> assert np.allclose(result['adj_close'], quandl_df['adj_close'])

    Note:
        - Most recent date: adjusted price = unadjusted price
        - Historical dates: adjusted using formula above
        - Volume is adjusted by cumulative split ratio only
    """
    if price_cols is None:
        price_cols = ["open", "high", "low", "close"]

    # Ensure data is sorted by date (oldest first)
    df = prices.sort("date").clone()

    # Convert to numpy for efficient backward iteration
    n = len(df)

    # Extract columns we need
    close_vals = df["close"].to_numpy()
    split_vals = df[split_col].to_numpy()
    div_vals = df[dividend_col].to_numpy()

    # Initialize adjusted prices
    adj_prices = {}
    for col in price_cols:
        if col in df.columns:
            adj_prices[col] = df[col].to_numpy().copy()

    # Detect which reverse splits have close prices adjusted for the split
    # Some data providers adjust close prices for reverse splits, others don't
    reverse_split_uses_ratio = {}
    for i in range(1, n):
        if split_vals[i] < 1.0:  # Reverse split
            close_today = close_vals[i]
            close_prev = close_vals[i - 1]
            expected_ratio = 1.0 / split_vals[i]
            actual_ratio = close_today / close_prev if close_prev > 0 else 0

            # If actual close change is within 20% of expected, assume it was adjusted
            if abs(actual_ratio - expected_ratio) / expected_ratio < 0.20:
                reverse_split_uses_ratio[i] = True
            else:
                reverse_split_uses_ratio[i] = False

    # Work BACKWARDS from newest (index n-1) to oldest (index 0)
    # The most recent date's adjusted price equals its unadjusted price
    # For each earlier date, apply the formula using the next day's values

    for i in range(n - 2, -1, -1):  # From second-to-last to first
        # Get next day's values (i+1)
        split_next = split_vals[i + 1]
        div_next = div_vals[i + 1]
        close_next = close_vals[i + 1]

        # Get today's close (used in formula for all columns)
        close_today = close_vals[i]

        # Calculate adjustment factor for all price columns
        # Different data providers encode reverse splits differently:
        # - Normal splits: always use split_ratio
        # - Reverse splits: use split_ratio only if close was mechanically adjusted
        if split_next >= 1.0:
            # Normal split: use split_ratio in formula
            adjustment_factor = (close_today / split_next - div_next) / close_next
        elif reverse_split_uses_ratio.get(i + 1, False):
            # Reverse split where close WAS adjusted: use split_ratio
            adjustment_factor = (close_today / split_next - div_next) / close_next
        else:
            # Reverse split where close was NOT adjusted: ignore split_ratio
            adjustment_factor = (close_today - div_next) / close_next

        for col in price_cols:
            if col in adj_prices:
                adj_next = adj_prices[col][i + 1]

                # Apply the adjustment formula
                adj_prices[col][i] = adj_next * adjustment_factor

    # Add adjusted price columns to dataframe
    for col, values in adj_prices.items():
        df = df.with_columns([pl.Series(name=f"adj_{col}", values=values)])

    # Adjust volume: multiply by cumulative split ratio (forward calculation)
    if volume_col and volume_col in df.columns:
        cumulative_split = df[split_col].cum_prod()
        df = df.with_columns([(pl.col(volume_col) * cumulative_split).alias(f"adj_{volume_col}")])

    return df


def apply_splits(
    prices: pl.DataFrame,
    split_col: str = "split_ratio",
    price_cols: list[str] | None = None,
    volume_col: str | None = "volume",
) -> pl.DataFrame:
    """Apply stock split adjustments to historical prices.

    DEPRECATED: For educational purposes. Use apply_corporate_actions() for
    production code, as it properly handles both splits and dividends together
    using the industry-standard methodology.

    This function uses a simplified cumulative product approach that works for
    splits in isolation but doesn't properly interact with dividend adjustments.

    Args:
        prices: DataFrame with date-sorted prices and split_ratio column
        split_col: Name of column containing split ratios (default: 'split_ratio')
        price_cols: List of price columns to adjust (default: ['open', 'high', 'low', 'close'])
        volume_col: Volume column name to adjust (multiplied by split ratio)

    Returns:
        DataFrame with split-adjusted prices
    """
    if price_cols is None:
        price_cols = ["open", "high", "low", "close"]

    # Create a copy to avoid modifying original
    df = prices.clone()

    # Calculate cumulative split factor (backward from most recent to oldest)
    # For each row, cumulative_factor = product of all split_ratios from that date forward
    df = df.with_columns(
        [pl.col(split_col).reverse().cum_prod().reverse().alias("_cumulative_split_factor")]
    )

    # Adjust prices: divide by cumulative split factor
    # Adjust volume: multiply by cumulative split factor
    adjustments = []

    for col in price_cols:
        if col in df.columns:
            adjustments.append(
                (pl.col(col) / pl.col("_cumulative_split_factor")).alias(f"adj_{col}")
            )

    if volume_col and volume_col in df.columns:
        adjustments.append(
            (pl.col(volume_col) * pl.col("_cumulative_split_factor")).alias(f"adj_{volume_col}")
        )

    df = df.with_columns(adjustments)

    # Drop temporary column
    df = df.drop("_cumulative_split_factor")

    return df


def apply_dividends(
    prices: pl.DataFrame,
    dividend_col: str = "ex-dividend",
    price_cols: list[str] | None = None,
    close_col: str = "adj_close",
) -> pl.DataFrame:
    """Apply dividend adjustments to historical prices (total return calculation).

    DEPRECATED: For educational purposes. Use apply_corporate_actions() for
    production code, as it properly handles both splits and dividends together
    using the industry-standard methodology.

    This function uses a simplified cumulative product approach that doesn't
    match the industry-standard iterative backward adjustment used by Quandl
    and Yahoo Finance.

    Args:
        prices: DataFrame with date-sorted prices and ex-dividend column
        dividend_col: Name of column containing dividend amounts
        price_cols: List of price columns to adjust
        close_col: Column to use for dividend factor calculation (default: 'adj_close')

    Returns:
        DataFrame with dividend-adjusted prices (total return series)
    """
    if price_cols is None:
        price_cols = ["adj_open", "adj_high", "adj_low", "adj_close"]

    df = prices.clone()

    # Calculate cumulative dividend adjustment factor
    # Factor = (1 - dividend/price) for each ex-dividend date
    # Cumulative product applied backward in time
    df = df.with_columns(
        [
            pl.when(pl.col(dividend_col) > 0)
            .then(1 - pl.col(dividend_col) / pl.col(close_col))
            .otherwise(1.0)
            .alias("_div_factor")
        ]
    )

    df = df.with_columns(
        [pl.col("_div_factor").reverse().cum_prod().reverse().alias("_cumulative_div_factor")]
    )

    # Adjust prices by dividing by cumulative dividend factor
    adjustments = []
    for col in price_cols:
        if col in df.columns:
            adjustments.append((pl.col(col) / pl.col("_cumulative_div_factor")).alias(col))

    df = df.with_columns(adjustments)

    # Drop temporary columns
    df = df.drop(["_div_factor", "_cumulative_div_factor"])

    return df
