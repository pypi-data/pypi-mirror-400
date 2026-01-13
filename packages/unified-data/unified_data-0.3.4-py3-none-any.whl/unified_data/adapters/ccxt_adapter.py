import ccxt
import polars as pl
from datetime import datetime
from .base import BaseAdapter
from ..models.enums import Columns, MarketType, TimeFramePeriod
from ..utils import get_logger

logger = get_logger("ccxt_adapter")

class CCXTAdapter(BaseAdapter):
    def get_kline(
        self, 
        ticker: str, 
        period: str, 
        start_date: datetime | None = None, 
        end_date: datetime | None = None, 
        limit: int = 100,
        market_type: MarketType | str | None = None
    ) -> pl.DataFrame:
        
        # 1. Parse ticker (BTC_USDT -> BTC/USDT)
        market_type = market_type or MarketType.CRYPTO
        symbol = self.get_exchange_symbol(ticker, market_type)
        
        # 2. Initialize Exchange (Default to Binance for now, or generic)
        # In a real app, this might come from config or the ticker string itself
        exchange = ccxt.binance()
        
        # 3. Handle Time parameters
        since = None
        if start_date:
            if isinstance(start_date, str):
                # Basic string parsing - could be improved
                try:
                    dt = datetime.fromisoformat(start_date)
                    since = int(dt.timestamp() * 1000)
                except ValueError:
                    logger.warning(f"Could not parse start_date: {start_date}")
            elif isinstance(start_date, datetime):
                since = int(start_date.timestamp() * 1000)

        # Convert period
        exchange_period = self.to_exchange_period(period)
        logger.info(f"Fetching {symbol} {exchange_period} from CCXT (since={since}, limit={limit})")
        
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=exchange_period, since=since, limit=limit)
        except Exception as e:
            logger.error(f"CCXT Error: {e}")
            raise

        if not ohlcv:
            logger.warning(f"No data returned for {symbol}")
            return pl.DataFrame()

        # 4. Convert to Polars DataFrame
        # CCXT returns: [timestamp, open, high, low, close, volume]
        data = {
            Columns.TIMESTAMP.value: [x[0] for x in ohlcv],
            Columns.OPEN.value: [x[1] for x in ohlcv],
            Columns.HIGH.value: [x[2] for x in ohlcv],
            Columns.LOW.value: [x[3] for x in ohlcv],
            Columns.CLOSE.value: [x[4] for x in ohlcv],
            Columns.VOLUME.value: [x[5] for x in ohlcv],
            Columns.SYMBOL.value: [ticker] * len(ohlcv)
        }
        
        df = pl.DataFrame(data)
        
        # Optional: Cast types if needed
        df = df.with_columns(
            pl.col(Columns.TIMESTAMP.value).cast(pl.Int64),
            pl.col(Columns.OPEN.value).cast(pl.Float64),
            pl.col(Columns.HIGH.value).cast(pl.Float64),
            pl.col(Columns.LOW.value).cast(pl.Float64),
            pl.col(Columns.CLOSE.value).cast(pl.Float64),
            pl.col(Columns.VOLUME.value).cast(pl.Float64)
        )

        return df

    def get_exchange_symbol(self, ticker: str, market_type: str) -> str:
        # Standard: BTC_USDT -> CCXT: BTC/USDT
        # Normalize
        ticker = ticker.upper()
        return ticker.replace("_", "/")

    def to_exchange_period(self, period: str) -> str:
        # Standard: 1d, 1w, 1M (Monthly)
        # CCXT: 1d, 1w, 1M (Monthly)
        
        if period == TimeFramePeriod.M1: # "1M"
            return "1M"
        if period == "1m": # Explicit minute handling if passed raw
             return "1m"
        if period == TimeFramePeriod.W1:
            return "1w"
        if period == TimeFramePeriod.D1:
            return "1d"
            
        # Default fallback
        return period
