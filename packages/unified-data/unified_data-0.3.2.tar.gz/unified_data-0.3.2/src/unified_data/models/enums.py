from enum import StrEnum

class MarketType(StrEnum):
    CRYPTO = "crypto"
    STOCK = "stock"
    FUTURES = "futures"

class Columns(StrEnum):
    """Standardized column names for the output DataFrame."""
    TIMESTAMP = "ts"
    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    VOLUME = "vol"
    SYMBOL = "symbol"
    EXCHANGE = "exchange"  # Useful when aggregating multiple sources

class Exchange(StrEnum):
    """Supported exchanges / sources."""
    BINANCE = "binance"
    CCXT = "ccxt"  # As a generic fallback or specific source
    YFINANCE = "yfinance"
    AKSHARE = "akshare"

class Status(StrEnum):
    OK = "OK"
    FAILED = "FAILED"
