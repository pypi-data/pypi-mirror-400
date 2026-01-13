import polars as pl
from datetime import datetime
from .models.enums import MarketType, Exchange, Columns, Status
from .models.types import KlineData
from .adapters.base import BaseAdapter
from .utils import get_logger

logger = get_logger("data_api")

def _get_adapter(market_type: str, exchange: str | None) -> tuple[BaseAdapter, str]:
    """Factory to get the correct adapter instance and the resolved exchange name."""
    
    # Default routing logic
    if exchange is None:
        if market_type == MarketType.CRYPTO:
            exchange = Exchange.CCXT
        elif market_type == MarketType.STOCK:
            exchange = Exchange.YFINANCE # Default to US stocks
            # Logic could be more complex here to detect China stocks if needed, 
            # but usually 'exchange' or specific logic handles it.
        elif market_type == MarketType.FUTURES:
            exchange = Exchange.YFINANCE
        else:
            raise ValueError(f"Unsupported market type: {market_type}")

    # Dispatch to specific adapters
    # Note: Imports are inside to avoid circular deps or heavy load if not needed
    if exchange == Exchange.CCXT:
        from .adapters.ccxt_adapter import CCXTAdapter
        return CCXTAdapter(), exchange
    elif exchange == Exchange.YFINANCE:
        from .adapters.yfinance_adapter import YFinanceAdapter
        return YFinanceAdapter(), exchange
    elif exchange == Exchange.AKSHARE:
        from .adapters.akshare_adapter import AKShareAdapter
        return AKShareAdapter(), exchange
    else:
        raise ValueError(f"Unsupported exchange: {exchange}")

def pull_kline(
    ticker: str, 
    market_type: str, 
    period: str, 
    start_date: datetime | str | None = None, 
    end_date: datetime | str | None = None, 
    limit: int = 200,
    exchange: str | None = None
) -> KlineData:
    """
    Main entry point to pull kline data.
    
    Args:
        ticker: Standardized ticker symbol.
        market_type: 'crypto', 'stock', 'futures' (use MarketType enum).
        period: Time period (e.g., '1d', '1h').
        start_date: Start datetime object or string.
        end_date: End datetime object or string.
        limit: Max records.
        exchange: Optional exchange name.

    Returns:
        KlineData: Object containing status, data (polars.DataFrame), and error message.
    """
    logger.info(f"Pulling kline for {ticker} ({market_type}) exchange={exchange}")
    
    try:
        adapter, exchange_name = _get_adapter(market_type, exchange)
        
        # Convert standard ticker to exchange symbol
        exchange_ticker = adapter.get_exchange_symbol(ticker, market_type)
        
        df = adapter.get_kline(exchange_ticker, period, start_date, end_date, limit)
        
        if df.is_empty():
             logger.warning(f"No data returned for {ticker}")
             return KlineData(status=Status.FAILED, error="No data returned", data=df)

        df = df.with_columns([
            pl.lit(exchange_name).alias(Columns.EXCHANGE.value),
            pl.lit(ticker).alias(Columns.SYMBOL.value)  # Ensure standard ticker is returned
        ])

        return KlineData(status=Status.OK, data=df)

    except Exception as e:
        logger.error(f"Failed to pull data: {e}")
        # Return empty dataframe on error for safety, or just default which is empty
        return KlineData(status=Status.FAILED, error=str(e))
