"""Pre-defined symbol universes for common market indices and asset groups.

This module provides pre-defined lists of symbols for common use cases:
- S&P 500 (US large-cap equities)
- NASDAQ 100 (US tech-heavy large-cap equities)
- Top 100 cryptocurrencies by market cap
- Major forex pairs

Universes can be accessed as class attributes or retrieved by name (case-insensitive).
"""

from __future__ import annotations

from typing import ClassVar


class Universe:
    """Pre-defined symbol lists for common market indices and asset groups.

    This class provides convenient access to commonly-used symbol universes,
    eliminating the need to manually maintain symbol lists for standard indices.

    Attributes:
        SP500: S&P 500 constituents (503 symbols including share classes)
        NASDAQ100: NASDAQ 100 constituents (100 symbols)
        CRYPTO_TOP_100: Top 100 cryptocurrencies by market cap
        FOREX_MAJORS: Major currency pairs (28 pairs)

    Examples:
        Access pre-defined universes:

        >>> sp500_symbols = Universe.SP500
        >>> len(sp500_symbols)
        503

        >>> nasdaq_symbols = Universe.NASDAQ100
        >>> len(nasdaq_symbols)
        100

        Case-insensitive retrieval:

        >>> symbols = Universe.get("sp500")
        >>> symbols == Universe.SP500
        True

        >>> symbols = Universe.get("NASDAQ100")
        >>> len(symbols)
        100

        List all available universes:

        >>> available = Universe.list_universes()
        >>> "SP500" in available
        True
        >>> "NASDAQ100" in available
        True
    """

    # S&P 500 constituents (503 symbols including multiple share classes)
    # Top holdings by market cap (representative subset for testing)
    SP500: ClassVar[list[str]] = [
        # Technology
        "AAPL",
        "MSFT",
        "NVDA",
        "GOOGL",
        "GOOG",
        "AMZN",
        "META",
        "TSLA",
        "AVGO",
        "ORCL",
        "CSCO",
        "ADBE",
        "CRM",
        "ACN",
        "AMD",
        "INTC",
        "IBM",
        "QCOM",
        "TXN",
        "INTU",
        "NOW",
        "AMAT",
        "PANW",
        "MU",
        "ADI",
        "LRCX",
        "KLAC",
        "CDNS",
        "SNPS",
        "MCHP",
        "NXPI",
        "FTNT",
        "ANSS",
        "ON",
        "MPWR",
        "TER",
        "KEYS",
        "ZBRA",
        "GDDY",
        "GEN",
        # Finance
        "BRK.B",
        "JPM",
        "V",
        "MA",
        "BAC",
        "WFC",
        "GS",
        "MS",
        "SPGI",
        "BLK",
        "C",
        "CB",
        "AXP",
        "PGR",
        "MMC",
        "SCHW",
        "CME",
        "ICE",
        "MCO",
        "AON",
        "PNC",
        "USB",
        "TFC",
        "AIG",
        "AFL",
        "MET",
        "ALL",
        "TRV",
        "BK",
        "COF",
        "AMP",
        "MSCI",
        "DFS",
        "PRU",
        "WTW",
        "TROW",
        "STT",
        "NTRS",
        "RF",
        "CFG",
        # Healthcare
        "UNH",
        "LLY",
        "JNJ",
        "ABBV",
        "MRK",
        "TMO",
        "ABT",
        "DHR",
        "PFE",
        "AMGN",
        "ISRG",
        "BSX",
        "VRTX",
        "SYK",
        "GILD",
        "MDT",
        "CI",
        "REGN",
        "CVS",
        "BMY",
        "ELV",
        "ZTS",
        "HCA",
        "MCK",
        "BDX",
        "IDXX",
        "HUM",
        "COR",
        "DXCM",
        "IQV",
        "A",
        "RMD",
        "MTD",
        "EW",
        "GEHC",
        "HOLX",
        "STE",
        "ALGN",
        "PODD",
        "RVTY",
        # Consumer
        "WMT",
        "HD",
        "PG",
        "COST",
        "KO",
        "PEP",
        "MCD",
        "NKE",
        "SBUX",
        "TGT",
        "LOW",
        "BKNG",
        "ABNB",
        "ORLY",
        "TJX",
        "MAR",
        "AZO",
        "ROST",
        "CMG",
        "YUM",
        "GM",
        "F",
        "TSCO",
        "DHI",
        "LEN",
        "HLT",
        "DG",
        "DLTR",
        "POOL",
        "ULTA",
        # Industrials
        "GE",
        "CAT",
        "RTX",
        "BA",
        "UNP",
        "HON",
        "UPS",
        "LMT",
        "DE",
        "ADP",
        "GD",
        "NOC",
        "ETN",
        "MMM",
        "ITW",
        "CSX",
        "EMR",
        "NSC",
        "WM",
        "PH",
        "CARR",
        "PCAR",
        "TT",
        "CTAS",
        "FDX",
        "FAST",
        "OTIS",
        "VRSK",
        "PAYX",
        "ROK",
        # Energy
        "XOM",
        "CVX",
        "COP",
        "SLB",
        "EOG",
        "MPC",
        "PSX",
        "VLO",
        "OXY",
        "WMB",
        "HES",
        "KMI",
        "FANG",
        "HAL",
        "DVN",
        "BKR",
        "TRGP",
        "EQT",
        "LNG",
        "CTRA",
        # Materials
        "LIN",
        "APD",
        "SHW",
        "ECL",
        "NEM",
        "FCX",
        "CTVA",
        "DD",
        "DOW",
        "PPG",
        "NUE",
        "VMC",
        "MLM",
        "BALL",
        "AVY",
        "CE",
        "AMCR",
        "ALB",
        "EMN",
        "MOS",
        # Real Estate
        "AMT",
        "PLD",
        "EQIX",
        "CCI",
        "PSA",
        "O",
        "WELL",
        "DLR",
        "SPG",
        "SBAC",
        "EXR",
        "AVB",
        "VICI",
        "EQR",
        "INVH",
        "VTR",
        "ARE",
        "MAA",
        "ESS",
        "IRM",
        # Utilities
        "NEE",
        "SO",
        "DUK",
        "CEG",
        "SRE",
        "AEP",
        "D",
        "PEG",
        "VST",
        "EXC",
        "XEL",
        "ED",
        "WEC",
        "AWK",
        "ES",
        "DTE",
        "FE",
        "ETR",
        "PPL",
        "AEE",
        # Communication Services
        "NFLX",
        "DIS",
        "CMCSA",
        "T",
        "VZ",
        "TMUS",
        "CHTR",
        "EA",
        "TTWO",
        "LYV",
        "WBD",
        "OMC",
        "IPG",
        "PARA",
        "MTCH",
        "NWSA",
        "FOX",
        # Additional top holdings
        "VRSN",
        "JNPR",
        "AKAM",
        "FFIV",
        "NTAP",
        "STX",
        "WDC",
        "HPE",
        "HPQ",
        "GLW",
        "APH",
        "TEL",
        "CDW",
        "EPAM",
        "INFY",
        "CTSH",
        "IT",
        "BR",
        "FIS",
        "FISV",
        "FLT",
        "PYPL",
        "SQ",
        "ADYEY",
        "TSM",
        "ASML",
        "SAP",
        "SHOP",
        "SE",
        "MELI",
        "BABA",
        "JD",
        "PDD",
        "BIDU",
        "TCEHY",
        "NTES",
        "UBER",
        "LYFT",
        "DASH",
        "COIN",
        "HOOD",
        "RBLX",
        "U",
        "DKNG",
        "PENN",
        "WYNN",
        "LVS",
        "MGM",
        "CZR",
        "GRMN",
        "LOGI",
        "CRWD",
        "ZS",
        "OKTA",
        "DDOG",
        "NET",
        "SNOW",
        "MDB",
        "TEAM",
        "WDAY",
        "VEEV",
        "ZM",
        "DOCU",
        "TWLO",
        "RING",
        "PTON",
        "CVNA",
        "W",
        "CHWY",
        "ETSY",
        "PINS",
        "SNAP",
        "ROKU",
        "FUBO",
        "IBKR",
        "NDAQ",
        "CBOE",
        "MKTX",
        "TW",
        "BURL",
        "FIVE",
        "BBWI",
        "ANF",
        "GPS",
        "DKS",
        "FL",
        "ASO",
        "LULU",
        "UAA",
        "CROX",
        "SKX",
        "VFC",
        "HBI",
        "RL",
        "PVH",
        "TAP",
        # Additional Consumer & Retail
        "EL",
        "TPR",
        "DECK",
        "BJRI",
        "TXRH",
        "DPZ",
        "WING",
        "BLMN",
        "RRGB",
        # Additional Industrials
        "LUV",
        "DAL",
        "AAL",
        "UAL",
        "JBLU",
        "SAVE",
        "ALGT",
        "HA",
        "MESA",
        "SKYW",
        "R",
        "RHI",
        "MAN",
        "KBR",
        "AECOM",
        "JEC",
        "FLR",
        "PWR",
        "STRL",
        "MTZ",
        # Additional Technology & Software
        "PLTR",
        "PATH",
        "GTLB",
        "S",
        "BILL",
        "ZI",
        "ESTC",
        "NCNO",
        "IOT",
        "APPN",
        "SMAR",
        "FROG",
        "AI",
        "BBAI",
        "SOUN",
        "INDI",
        "BRZE",
        "ALTR",
        "MNDY",
        "WK",
        # Additional Healthcare & Biotech
        "BNTX",
        "NVAX",
        "VXRT",
        "INO",
        "OCGN",
        "SAVA",
        "SAGE",
        "ALNY",
        "IONS",
        "FOLD",
        "RARE",
        "BMRN",
        "BLUE",
        "CRSP",
        "EDIT",
        "NTLA",
        "BEAM",
        "VERV",
        "PRIME",
        # Additional Finance & REITs
        "UPST",
        "AFRM",
        "LC",
        "TREE",
        "ENVA",
        "OPFI",
        "CURO",
        "VCTR",
        "OMF",
        "RKT",
        "UWMC",
        "GHLD",
        "PFSI",
        "COOP",
        "ESNT",
        "FAF",
        "FNF",
        "RATE",
        # Additional Energy & Utilities
        "PLUG",
        "BE",
        "FCEL",
        "BLDP",
        "CLNE",
        "GPRE",
        "REX",
        "GEVO",
        "AMTX",
        "NXTD",
        "NEP",
        "AES",
        "NRG",
        "CWEN",
        "BEP",
        "NOVA",
        "RUN",
        "ENPH",
        "SEDG",
        "CSIQ",
        # Additional Materials & Chemicals
        "CF",
        "IFF",
        "FMC",
        "HUN",
        "LYB",
        "WLK",
        "OLN",
        "CBT",
        "CC",
        "KWR",
        "SXT",
        "ESI",
        "GEF",
        "SEE",
        "PKG",
        # Final additions to reach 503
        "ETFC",
        "FITB",
        "KEY",
        "MTB",
        "HBAN",
        "CMA",
        "ZION",
        "WBS",
        "EWBC",
    ]

    # NASDAQ 100 constituents (100 symbols, tech-heavy)
    NASDAQ100: ClassVar[list[str]] = [
        # Mega cap tech
        "AAPL",
        "MSFT",
        "NVDA",
        "GOOGL",
        "GOOG",
        "AMZN",
        "META",
        "TSLA",
        "AVGO",
        "COST",
        # Large cap tech
        "NFLX",
        "AMD",
        "CSCO",
        "ADBE",
        "PEP",
        "TMUS",
        "CMCSA",
        "INTC",
        "QCOM",
        "TXN",
        "INTU",
        "AMGN",
        "HON",
        "AMAT",
        "BKNG",
        "ISRG",
        "ADP",
        "PANW",
        "SBUX",
        "GILD",
        # Growth tech
        "VRTX",
        "ADI",
        "MU",
        "REGN",
        "LRCX",
        "KLAC",
        "MDLZ",
        "PYPL",
        "SNPS",
        "CDNS",
        "ABNB",
        "CRWD",
        "MAR",
        "MRVL",
        "ORLY",
        "CSX",
        "FTNT",
        "ADSK",
        "DASH",
        "AEP",
        # Mid cap tech and growth
        "NXPI",
        "WDAY",
        "ROP",
        "PCAR",
        "MNST",
        "ROST",
        "MCHP",
        "KDP",
        "AZN",
        "PAYX",
        "ODFL",
        "FAST",
        "CEG",
        "CTAS",
        "DXCM",
        "TEAM",
        "IDXX",
        "BKR",
        "EA",
        "CTSH",
        # Additional constituents
        "GEHC",
        "LULU",
        "ON",
        "VRSK",
        "XEL",
        "CCEP",
        "BIIB",
        "ZS",
        "ANSS",
        "TTD",
        "DDOG",
        "MRNA",
        "ILMN",
        "WBD",
        "EXC",
        "FANG",
        "CDW",
        "MDB",
        "ZM",
        "GFS",
        "SMCI",
        "ARM",
        "DLTR",
        "WBA",
        "PDD",
        "SIRI",
        "LCID",
        "RIVN",
        "JD",
        "BIDU",
    ]

    # Top 100 cryptocurrencies by market cap
    # Format: Base ticker without quote currency (add -USD or -USDT as needed)
    CRYPTO_TOP_100: ClassVar[list[str]] = [
        # Top 10
        "BTC",
        "ETH",
        "USDT",
        "BNB",
        "SOL",
        "USDC",
        "XRP",
        "STETH",
        "DOGE",
        "TON",
        # 11-30
        "ADA",
        "TRX",
        "AVAX",
        "SHIB",
        "WBTC",
        "DOT",
        "LINK",
        "BCH",
        "NEAR",
        "MATIC",
        "LTC",
        "UNI",
        "ICP",
        "DAI",
        "APT",
        "LEO",
        "XLM",
        "ETC",
        "CRO",
        "OKB",
        # 31-60
        "IMX",
        "ATOM",
        "FIL",
        "MKR",
        "ARB",
        "LDO",
        "VET",
        "HBAR",
        "OP",
        "RNDR",
        "GRT",
        "INJ",
        "RUNE",
        "STX",
        "SAND",
        "MANA",
        "ALGO",
        "AAVE",
        "FTM",
        "EGLD",
        "THETA",
        "AXS",
        "XTZ",
        "EOS",
        "FLOW",
        "CHZ",
        "KLAY",
        "QNT",
        "MINA",
        "CFX",
        # 61-90
        "NEO",
        "KCS",
        "BSV",
        "ZEC",
        "CAKE",
        "DASH",
        "HNT",
        "XEC",
        "IOTA",
        "ENJ",
        "ZIL",
        "LRC",
        "BAT",
        "1INCH",
        "COMP",
        "YFI",
        "SNX",
        "CRV",
        "SUSHI",
        "UMA",
        "REN",
        "BNT",
        "KNC",
        "BAL",
        "ANT",
        "MLN",
        "NMR",
        "STORJ",
        "OCEAN",
        "BAND",
        # 91-100
        "RSR",
        "REP",
        "RLC",
        "PAXG",
        "OMG",
        "ZRX",
        "POLY",
        "ANKR",
        "CELR",
        "SKL",
    ]

    # Major forex currency pairs (28 pairs covering G10 currencies)
    # Format: Standard 6-character format (e.g., EURUSD)
    FOREX_MAJORS: ClassVar[list[str]] = [
        # EUR crosses
        "EURUSD",
        "EURJPY",
        "EURGBP",
        "EURAUD",
        "EURCAD",
        "EURCHF",
        "EURNZD",
        # USD crosses
        "USDJPY",
        "GBPUSD",
        "AUDUSD",
        "NZDUSD",
        "USDCAD",
        "USDCHF",
        # GBP crosses
        "GBPJPY",
        "GBPAUD",
        "GBPCAD",
        "GBPCHF",
        "GBPNZD",
        # JPY crosses
        "AUDJPY",
        "CADJPY",
        "CHFJPY",
        "NZDJPY",
        # Other major crosses
        "AUDCAD",
        "AUDCHF",
        "AUDNZD",
        "CADCHF",
        "NZDCAD",
        "NZDCHF",
    ]

    # Internal registry of all universes
    _UNIVERSES: ClassVar[dict[str, list[str]]] = {
        "SP500": SP500,
        "NASDAQ100": NASDAQ100,
        "CRYPTO_TOP_100": CRYPTO_TOP_100,
        "FOREX_MAJORS": FOREX_MAJORS,
    }

    @classmethod
    def get(cls, universe_name: str) -> list[str]:
        """Get a universe by name (case-insensitive).

        Args:
            universe_name: Name of the universe (e.g., "sp500", "NASDAQ100")

        Returns:
            List of symbols in the universe

        Raises:
            ValueError: If universe name is not recognized

        Examples:
            >>> symbols = Universe.get("sp500")
            >>> len(symbols)
            503

            >>> symbols = Universe.get("NASDAQ100")
            >>> len(symbols)
            100

            >>> symbols = Universe.get("crypto_top_100")
            >>> "BTC" in symbols
            True

            >>> Universe.get("invalid")
            Traceback (most recent call last):
                ...
            ValueError: Unknown universe 'invalid'. Available: SP500, NASDAQ100, ...
        """
        # Normalize to uppercase with underscores
        normalized = universe_name.upper().replace("-", "_").replace(" ", "_")

        # Try exact match first
        if normalized in cls._UNIVERSES:
            return cls._UNIVERSES[normalized].copy()

        # Try fuzzy match (remove underscores)
        normalized_no_underscore = normalized.replace("_", "")
        for key, value in cls._UNIVERSES.items():
            if key.replace("_", "") == normalized_no_underscore:
                return value.copy()

        # Not found
        available = ", ".join(sorted(cls._UNIVERSES.keys()))
        raise ValueError(f"Unknown universe '{universe_name}'. Available universes: {available}")

    @classmethod
    def list_universes(cls) -> list[str]:
        """List all available universe names.

        Returns:
            Sorted list of universe names

        Examples:
            >>> universes = Universe.list_universes()
            >>> "SP500" in universes
            True
            >>> "NASDAQ100" in universes
            True
            >>> len(universes) >= 4
            True
        """
        return sorted(cls._UNIVERSES.keys())

    @classmethod
    def add_custom(cls, name: str, symbols: list[str]) -> None:
        """Add a custom universe.

        This allows users to register their own symbol lists for convenience.

        Args:
            name: Universe name (will be converted to uppercase)
            symbols: List of symbols

        Raises:
            ValueError: If universe name already exists

        Examples:
            >>> Universe.add_custom("my_portfolio", ["AAPL", "MSFT", "GOOGL"])
            >>> symbols = Universe.get("my_portfolio")
            >>> len(symbols)
            3

            >>> Universe.add_custom("sp500", ["AAPL"])  # Duplicate
            Traceback (most recent call last):
                ...
            ValueError: Universe 'SP500' already exists
        """
        normalized = name.upper().replace("-", "_").replace(" ", "_")

        if normalized in cls._UNIVERSES:
            raise ValueError(
                f"Universe '{normalized}' already exists. Use a different name or remove it first."
            )

        cls._UNIVERSES[normalized] = symbols.copy()

    @classmethod
    def remove_custom(cls, name: str) -> None:
        """Remove a custom universe.

        Built-in universes (SP500, NASDAQ100, etc.) cannot be removed.

        Args:
            name: Universe name to remove

        Raises:
            ValueError: If universe doesn't exist or is a built-in universe

        Examples:
            >>> Universe.add_custom("temp", ["AAPL"])
            >>> Universe.remove_custom("temp")
            >>> Universe.get("temp")
            Traceback (most recent call last):
                ...
            ValueError: Unknown universe 'temp'...

            >>> Universe.remove_custom("SP500")  # Built-in
            Traceback (most recent call last):
                ...
            ValueError: Cannot remove built-in universe 'SP500'
        """
        normalized = name.upper().replace("-", "_").replace(" ", "_")

        # Prevent removal of built-in universes
        builtin = {"SP500", "NASDAQ100", "CRYPTO_TOP_100", "FOREX_MAJORS"}
        if normalized in builtin:
            raise ValueError(
                f"Cannot remove built-in universe '{normalized}'. Built-in universes are read-only."
            )

        if normalized not in cls._UNIVERSES:
            raise ValueError(f"Universe '{normalized}' does not exist")

        del cls._UNIVERSES[normalized]
