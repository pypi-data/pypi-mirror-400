import sys
import os
import unittest

from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from unified_data.api import pull_kline
from unified_data.models.enums import MarketType, Exchange, Columns

class TestEndToEnd(unittest.TestCase):
    """
    End-to-end tests for the data API.
    These tests use the high-level `pull_kline` entry point.
    """

    def _get_china_futures_front_month(self, symbol="AU"):
        """Helper to guess a valid 'active' contract for China futures."""
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

    def test_e2e_us_stock_yfinance(self):
        """Test E2E flow for US Stock (YFinance)."""
        ticker = "MSFT"
        res = pull_kline(
            ticker=ticker,
            market_type=MarketType.STOCK,
            period="1d",
            limit=5,
            exchange=Exchange.YFINANCE
        )
        df = res.data
        self.assertFalse(df.is_empty(), "US Stock data should not be empty")
        self.assertEqual(df[Columns.SYMBOL.value][0], ticker)
        print(f"\n[E2E US Stock] Fetched {len(df)} rows for {ticker}")

    def test_e2e_crypto_ccxt(self):
        """Test E2E flow for Crypto (CCXT/Binance)."""
        ticker = "ETH_USDT"
        res = pull_kline(
            ticker=ticker,
            market_type=MarketType.CRYPTO,
            period="1d",
            limit=5,
            exchange=Exchange.CCXT
        )
        df = res.data
        self.assertFalse(df.is_empty(), "Crypto data should not be empty")
        self.assertEqual(df[Columns.SYMBOL.value][0], ticker)
        print(f"\n[E2E Crypto] Fetched {len(df)} rows for {ticker}")

    def test_e2e_china_stock_akshare(self):
        """Test E2E flow for China Stock (AKShare)."""
        ticker = "600519" # Kweichow Moutai
        res = pull_kline(
            ticker=ticker,
            market_type=MarketType.STOCK,
            period="daily",
            limit=5,
            exchange=Exchange.AKSHARE
        )
        df = res.data
        self.assertFalse(df.is_empty(), "China Stock data should not be empty")
        self.assertEqual(df[Columns.SYMBOL.value][0], ticker)
        print(f"\n[E2E China Stock] Fetched {len(df)} rows for {ticker}")

    def test_e2e_us_futures_yfinance(self):
        """Test E2E flow for US Futures (YFinance)."""
        ticker = "ES=F" # S&P 500 Futures
        res = pull_kline(
            ticker=ticker,
            market_type=MarketType.FUTURES,
            period="1d",
            limit=5,
            exchange=Exchange.YFINANCE
        )
        df = res.data
        self.assertFalse(df.is_empty(), "US Futures data should not be empty")
        self.assertEqual(df[Columns.SYMBOL.value][0], ticker)
        print(f"\n[E2E US Futures] Fetched {len(df)} rows for {ticker}")

    def test_e2e_china_futures_akshare(self):
        """Test E2E flow for China Futures (AKShare)."""
        ticker = self._get_china_futures_front_month("RB") # Rebar Futures
        res = pull_kline(
            ticker=ticker,
            market_type=MarketType.FUTURES,
            period="daily",
            limit=5,
            exchange=Exchange.AKSHARE
        )
        df = res.data
        self.assertFalse(df.is_empty(), "China Futures data should not be empty")
        self.assertEqual(df[Columns.SYMBOL.value][0], ticker)
        print(f"\n[E2E China Futures] Fetched {len(df)} rows for {ticker}")

if __name__ == '__main__':
    unittest.main()
