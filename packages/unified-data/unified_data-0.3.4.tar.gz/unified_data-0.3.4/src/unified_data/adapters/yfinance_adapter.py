import yfinance as yf
import polars as pl
from datetime import datetime
from .base import BaseAdapter
from ..models.enums import Columns, MarketType, TimeFramePeriod
from ..utils import get_logger, calculate_start_date

logger = get_logger("yfinance_adapter")

class YFinanceAdapter(BaseAdapter):
    def get_kline(
        self, 
        ticker: str, 
        period: str, 
        start_date: datetime | None = None, 
        end_date: datetime | None = None, 
        limit: int = 200,
        market_type: MarketType | str | None = None
    ) -> pl.DataFrame:
        
        # 1. Ticker is usually consistent (AAPL, GC=F), but ensure safe string
        market_type = market_type or MarketType.STOCK
        symbol = self.get_exchange_symbol(ticker, market_type)
        
        logger.info(f"Fetching {symbol} {period} from YFinance")
        
        try:
            # YF usage: Ticker.history(period, interval, start, end, auto_adjust, actions)
            # This is more robust than yf.download and returns a single-level index by default
            
            # Check for valid interval
            # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            
            interval = self.to_exchange_period(period)
            
            if not end_date:
                end_date = datetime.now()
            
            if not start_date:
                start_date = calculate_start_date(end_date, limit, period)
            
            # Create Ticker object
            ticker_obj = yf.Ticker(symbol)
            
            # Fetch history
            # auto_adjust=True handles splits/dividends and returns 'Close' as adjusted
            pdf = ticker_obj.history(
                interval=interval,
                start=start_date,
                end=end_date,
                auto_adjust=True
            )
            
            if pdf.empty:
                logger.warning(f"No data returned for {symbol}")
                return pl.DataFrame()
                
            # yf.Ticker.history returns a DataFrame with DatetimeIndex
            # Columns are typically: Open, High, Low, Close, Volume, Dividends, Stock Splits
            # It comes flattened (no MultiIndex) for single ticker
            
            # Reset index to get Date/Datetime as column
            pdf = pdf.reset_index()
            
            # 2. Convert to Polars
            df = pl.from_pandas(pdf)
            
            # 3. Standardize Columns
            # YF cols: Date (or Datetime), Open, High, Low, Close, Adj Close, Volume
            # Standardize names to lowercase first to be safe
            df = df.select(pl.all().name.to_lowercase())
            
            # Rename map
            rename_map = {
                "date": Columns.TIMESTAMP.value,
                "datetime": Columns.TIMESTAMP.value,
                "open": Columns.OPEN.value,
                "high": Columns.HIGH.value,
                "low": Columns.LOW.value,
                "close": Columns.CLOSE.value,
                "volume": Columns.VOLUME.value,
            }
            
            # Filter valid keys that exist in df
            existing_cols = df.columns
            final_map = {k: v for k, v in rename_map.items() if k in existing_cols}
            
            df = df.rename(final_map)
            
            # Ensure TIMESTAMP is proper int (ms) if it's datetime
            # YF usually gives Date or Datetime
            if Columns.TIMESTAMP.value in df.columns:
                df = df.with_columns(
                   pl.col(Columns.TIMESTAMP.value).cast(pl.Datetime).dt.timestamp("ms").alias(Columns.TIMESTAMP.value)
                )

            # Add Symbol
            df = df.with_columns(pl.lit(ticker).alias(Columns.SYMBOL.value))
            
            # Select only required columns (handling missing optional ones gracefully if needed)
            # For now select strictly
            required = [
                Columns.TIMESTAMP.value, 
                Columns.OPEN.value, 
                Columns.HIGH.value, 
                Columns.LOW.value, 
                Columns.CLOSE.value, 
                Columns.VOLUME.value,
                Columns.SYMBOL.value
            ]
            
            df = df.select([c for c in required if c in df.columns])
            
            # Apply limit
            if limit > 0:
                df = df.tail(limit)

            return df

        except Exception as e:
            logger.error(f"YFinance Error: {e}")
            raise

    def get_exchange_symbol(self, ticker: str, market_type: str) -> str:
        # Standard: AAPL -> AAPL
        # Standard: GC=F -> GC=F
        # Standard: BTC_USDT -> BTC-USD (if we supported crypto via YF)
        
        # Normalize to upper
        ticker = ticker.upper()
        
        if market_type == MarketType.CRYPTO and "_" in ticker:
             return ticker.replace("_", "-")
             
        # For stocks and futures, usually standard is close enough to YF
        # e.g. GC=F is standard and YF expects GC=F
        return ticker

    def to_exchange_period(self, period: str) -> str:
        # Standard: 1d, 1w, 1M
        # YF: 1d, 1wk, 1mo
        
        if period == TimeFramePeriod.M1 or period == "1M":
            return "1mo"
        if period == TimeFramePeriod.W1:
            return "1wk"
        if period == TimeFramePeriod.D1:
            return "1d"
            
        return period

if __name__ == "__main__":
    adapter = YFinanceAdapter()
    print("Fetching AAPL")
    df = adapter.get_kline("AAPL", "1d")
    print(df)
