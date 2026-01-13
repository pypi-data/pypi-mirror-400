
from ..models.enums import Columns, MarketType
from datetime import datetime
import polars as pl
from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    """Abstract base class for all data source adapters."""
    
    @abstractmethod
    def get_kline(
        self, 
        ticker: str, 
        period: str, 
        start_date: datetime | None = None, 
        end_date: datetime | None = None, 
        limit: int = 100,
        market_type: MarketType | str | None = None
    ) -> pl.DataFrame:
        """
        Fetch kline data and return a standardized Polars DataFrame.
        
        Must return DataFrame with columns strictly matching enum.Columns.
        """
        pass

    @abstractmethod
    def get_exchange_symbol(self, ticker: str, market_type: MarketType | str) -> str:
        """
        Convert standard ticker to exchange-specific symbol.
        
        Args:
            ticker: Standardized ticker (e.g., "BTC_USDT", "RB=F").
            market_type: Market type (crypto, stock, futures).
            
        Returns:
            Exchange specific symbol (e.g., "BTC/USDT", "RB0").
        """
        pass

    @abstractmethod
    def to_exchange_period(self, period: str) -> str:
        """
        Convert standard period to exchange-specific period.
        
        Args:
            period: Standard period (e.g. "1d", "1w", "1m").
            
        Returns:
            Exchange specific period string.
        """
        pass

    def standardize_columns(self, df: pl.DataFrame) -> pl.DataFrame:
        """Helper to ensure columns match the standard."""
        # This is a placeholder; implementations might enforce this 
        # or we check it in the main entry.
        # Basic check logic can go here
        return df
