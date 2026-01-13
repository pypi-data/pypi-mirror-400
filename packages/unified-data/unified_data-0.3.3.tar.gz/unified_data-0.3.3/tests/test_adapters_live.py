import sys
import os
import unittest
import polars as pl
from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from unified_data.adapters.akshare_adapter import AKShareAdapter
from unified_data.adapters.ccxt_adapter import CCXTAdapter
from unified_data.adapters.yfinance_adapter import YFinanceAdapter
from unified_data.models.enums import Columns

class TestAdaptersLive(unittest.TestCase):
    """
    Live tests for adapters. 
    These tests hit the real external APIs. 
    Failures might occur due to network issues or API changes.
    """

    def setUp(self):
        # Common setup if needed
        pass

    def _get_china_futures_front_month(self, symbol="AU"):
        """
        Helper to guess a valid 'active' contract for China futures.
        Strategies:
        1. Current month + 1 month.
        2. Or major months (Jan, May, Sep).
        
        For simplicity, let's pick the "Next Month" to ensure it hasn't expired 
        at the start of the month, but is close enough to be 'front'.
        """
        now = datetime.now()
        # Move to next month
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1)
        else:
            next_month = now.replace(month=now.month + 1)
            
        # Format: YYMM
        y_str = str(next_month.year)[-2:]
        m_str = f"{next_month.month:02d}"
        
        return f"{symbol}{y_str}{m_str}"

    def test_akshare_adapter_live_stock(self):
        """Test fetching A-Share stock data from AKShare."""
        adapter = AKShareAdapter()
        # "000001" is Ping An Bank
        ticker = "000001"
        period = "daily" 
        
        try:
            df = adapter.get_kline(ticker=ticker, period=period, limit=10)
            
            print(f"\n[AKShare Stock] Fetched {len(df)} rows.")
            
            self.assertIsInstance(df, pl.DataFrame)
            self.assertFalse(df.is_empty(), "Returned DataFrame should not be empty")
            
            # Check columns
            expected_cols = [
                Columns.TIMESTAMP.value, 
                Columns.OPEN.value, 
                Columns.HIGH.value, 
                Columns.LOW.value, 
                Columns.CLOSE.value, 
                Columns.VOLUME.value,
                Columns.SYMBOL.value
            ]
            for col in expected_cols:
                self.assertIn(col, df.columns)
                
            # Check symbol
            self.assertEqual(df[Columns.SYMBOL.value][0], ticker)

        except Exception as e:
            self.fail(f"AKShare live test failed with error: {e}")

    def test_akshare_adapter_live_futures(self):
        """Test fetching Futures data from AKShare (Front Month)."""
        adapter = AKShareAdapter()
        # Use helper to get a likely valid front-ish month contract for Gold (AU)
        ticker = self._get_china_futures_front_month("AU")
        period = "daily" 

        
        try:
            print(f"\n[AKShare Futures] Requesting ticker: {ticker}")
            df = adapter.get_kline(ticker=ticker, period=period, limit=10)
            
            print(f"[AKShare Futures] Fetched {len(df)} rows.")
            
            self.assertIsInstance(df, pl.DataFrame)
            self.assertFalse(df.is_empty(), "Returned DataFrame should not be empty")
            
            # Check symbol
            self.assertEqual(df[Columns.SYMBOL.value][0], ticker)

        except Exception as e:
            self.fail(f"AKShare Futures live test failed with error: {e}")

    def test_ccxt_adapter_live_crypto(self):
        """Test fetching Crypto data from CCXT (Binance)."""
        adapter = CCXTAdapter()
        ticker = "BTC_USDT"
        period = "1d"
        
        try:
            df = adapter.get_kline(ticker=ticker, period=period, limit=5)
            
            print(f"\n[CCXT Crypto] Fetched {len(df)} rows.")
            
            self.assertIsInstance(df, pl.DataFrame)
            self.assertFalse(df.is_empty(), "Returned DataFrame should not be empty")
            
            # Check columns
            expected_cols = [
                Columns.TIMESTAMP.value, 
                Columns.OPEN.value, 
                Columns.HIGH.value, 
                Columns.LOW.value, 
                Columns.CLOSE.value, 
                Columns.VOLUME.value,
                Columns.SYMBOL.value
            ]
            for col in expected_cols:
                self.assertIn(col, df.columns)
                
            # Check symbol
            self.assertEqual(df[Columns.SYMBOL.value][0], ticker)
            
        except Exception as e:
            self.fail(f"CCXT live test failed with error: {e}")

    def test_yfinance_adapter_live_stock(self):
        """Test fetching Stock data from YFinance."""
        adapter = YFinanceAdapter()
        ticker = "AAPL"
        period = "1d"
        print("starting test_yfinance_adapter_live_stock")
        try:
            df = adapter.get_kline(ticker=ticker, period=period, limit=5)
            
            print(f"\n[YFinance Stock] Fetched {len(df)} rows.")
            
            self.assertIsInstance(df, pl.DataFrame)
            self.assertFalse(df.is_empty(), "Returned DataFrame should not be empty")
            
            # Check columns
            expected_cols = [
                Columns.TIMESTAMP.value, 
                Columns.OPEN.value, 
                Columns.HIGH.value, 
                Columns.LOW.value, 
                Columns.CLOSE.value, 
                Columns.VOLUME.value,
                Columns.SYMBOL.value
            ]
            for col in expected_cols:
                self.assertIn(col, df.columns)
                
            # Check symbol
            self.assertEqual(df[Columns.SYMBOL.value][0], ticker)
            
        except Exception as e:
            self.fail(f"YFinance live test failed with error: {e}")

    def test_yfinance_adapter_live_futures(self):
        """Test fetching Futures data from YFinance (Front Month)."""
        adapter = YFinanceAdapter()
        # GC=F is Gold Futures Front Month
        ticker = "GC=F"
        period = "1d"
        
        try:
            df = adapter.get_kline(ticker=ticker, period=period, limit=5)

            print(f"\n[YFinance Futures] Fetched {len(df)} rows.")
            
            self.assertIsInstance(df, pl.DataFrame)
            self.assertFalse(df.is_empty(), "Returned DataFrame should not be empty")
            
            # Check symbol
            self.assertEqual(df[Columns.SYMBOL.value][0], ticker)
            
        except Exception as e:
            self.fail(f"YFinance Futures live test failed with error: {e}")

if __name__ == '__main__':
    unittest.main()
