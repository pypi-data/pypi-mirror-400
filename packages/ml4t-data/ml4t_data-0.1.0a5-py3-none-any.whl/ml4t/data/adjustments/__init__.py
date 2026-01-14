"""Corporate actions and price adjustment utilities.

This module provides utilities for adjusting historical stock prices for
corporate actions (splits and dividends), useful for creating continuous
price series and demonstrating proper data handling in backtesting.

Educational Purpose:
    Show readers of ML4T how to:
    - Apply stock split adjustments to unadjusted prices
    - Apply dividend adjustments (total return calculation)
    - Validate adjustment logic against known-good data (Quandl)
    - Chain data from multiple sources with different adjustment conventions

Example:
    >>> from ml4t.data.adjustments import apply_splits, apply_dividends
    >>>
    >>> # Apply splits to unadjusted prices
    >>> adjusted_prices = apply_splits(
    ...     prices=unadjusted_df,
    ...     splits=splits_df,
    ...     price_cols=['open', 'high', 'low', 'close']
    ... )
    >>>
    >>> # Validate against Quandl's pre-calculated adjusted prices
    >>> assert np.allclose(adjusted_prices['close'], quandl_adj_close)
"""

from .core import (
    apply_corporate_actions,
    apply_dividends,
    apply_splits,
)

__all__ = [
    "apply_splits",
    "apply_dividends",
    "apply_corporate_actions",
]
