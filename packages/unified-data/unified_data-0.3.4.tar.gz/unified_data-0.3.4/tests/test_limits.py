import sys
import os
import unittest
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from unified_data.api import pull_kline
from unified_data.models.enums import MarketType, Exchange

class TestLimits(unittest.TestCase):
    """
    Consolidated tests for the 'limit' parameter across different vendors and edge cases.
    Combines logic from old test_limit_logic.py and test_limit_advanced.py.
    """

    # --- Basic Logic Tests ---
    def test_crypto_limit(self):
        """Test crypto kline respects limit (CCXT)."""
        limit = 10
        res = pull_kline("BTC_USDT", MarketType.CRYPTO, "1d", limit=limit)
        df = res.data
        self.assertEqual(len(df), limit)

    def test_stock_limit_yfinance(self):
        """Test stock kline respects limit (YFinance)."""
        limit = 50
        res = pull_kline("AAPL", MarketType.STOCK, "1d", limit=limit)
        df = res.data
        self.assertEqual(len(df), limit)

    def test_stock_limit_akshare(self):
        """Test stock kline respects limit (AKShare)."""
        limit = 20
        # "000001" is Ping An Bank
        res = pull_kline(
            ticker="000001",
            market_type=MarketType.STOCK,
            period="daily",
            limit=limit,
            exchange=Exchange.AKSHARE
        )
        df = res.data
        self.assertEqual(len(df), limit)

    def test_default_limit(self):
        """Test default limit is 200."""
        res = pull_kline("BTC_USDT", MarketType.CRYPTO, "1d")
        df = res.data
        self.assertEqual(len(df), 200)

    # --- Advanced/Edge Case Tests ---
    def test_limit_one(self):
        """Verify limit=1 returns exactly one row."""
        for mt in [MarketType.CRYPTO, MarketType.STOCK]:
            ticker = "BTC_USDT" if mt == MarketType.CRYPTO else "AAPL"
            res = pull_kline(ticker, mt, "1d", limit=1)
            df = res.data
            self.assertEqual(len(df), 1, f"Failed for {mt} with limit=1")

    def test_limit_large(self):
        """Verify limit=500 (larger than default) works."""
        res = pull_kline("AAPL", MarketType.STOCK, "1d", limit=500)
        df = res.data
        self.assertEqual(len(df), 500)

    def test_limit_intraday(self):
        """Verify limit works with intraday periods."""
        # CCXT supports 1h easily
        res = pull_kline("BTC_USDT", MarketType.CRYPTO, "1h", limit=50)
        df = res.data
        self.assertEqual(len(df), 50)

    def test_limit_and_start_date_combined(self):
        """
        Verify that when both start_date and limit are provided, 
        limit acts as a tail on the resulting range.
        Fetch 100 days of data but limit to 5.
        """
        end = datetime.now()
        start = end - timedelta(days=100)
        
        # Proper call logic that was broken in previous file
        res = pull_kline(
            "AAPL", 
            MarketType.STOCK, 
            "1d", 
            start_date=start, 
            end_date=end, 
            limit=5
        )
        df = res.data
        self.assertEqual(len(df), 5)
        
    def test_limit_exceeding_availability(self):
        """
        Verify behavior when limit is larger than available data.
        """
        # AAPL likely has > 10000 days? 10000 days is ~27 years (1997). Use 10k limit.
        res = pull_kline("AAPL", MarketType.STOCK, "1d", limit=10000)
        df = res.data
        # Just ensure it doesn't crash and returns something
        self.assertTrue(len(df) > 0)
        self.assertTrue(len(df) <= 10000)

if __name__ == "__main__":
    unittest.main()
