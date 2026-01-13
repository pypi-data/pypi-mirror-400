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
from unified_data.models.enums import Columns, MarketType

class TestStandardSymbolLive(unittest.TestCase):
    """
    Test standard symbol handling with mixed case normaliztion.
    """

    def test_akshare_futures_china_mixed_case(self):
        """Test 'Rb=F' normalization to 'RB0'."""
        adapter = AKShareAdapter()
        ticker = "Rb=F"
        period = "daily" 
        
        print(f"\n[AKShare Futures] Testing mixed case: {ticker}")
        df = adapter.get_kline(ticker=ticker, period=period, limit=5, market_type=MarketType.FUTURES)
        
        self.assertFalse(df.is_empty(), "Should return data for Rb=F")
        # Check if the symbol column in output uses the input ticker (which is standard behavior) or standardized
        # Usually adapters return the input ticker in the symbol column.
        self.assertEqual(df[Columns.SYMBOL.value][0], ticker) 

    def test_yfinance_futures_usa_mixed_case(self):
        """Test 'GC=f' normalization to 'GC=F'."""
        adapter = YFinanceAdapter()
        ticker = "GC=f"
        period = "1d"
        
        print(f"\n[YFinance Futures] Testing mixed case: {ticker}")
        df = adapter.get_kline(ticker=ticker, period=period, limit=5, market_type=MarketType.FUTURES)
        
        self.assertFalse(df.is_empty(), "Should return data for GC=f")
        self.assertEqual(df[Columns.SYMBOL.value][0], ticker)

    def test_ccxt_crypto_mixed_case(self):
        """Test 'ETH_UsDT' normalization to 'ETH/USDT'."""
        adapter = CCXTAdapter()
        ticker = "ETH_UsDT"
        period = "1d"
        
        print(f"\n[CCXT Crypto] Testing mixed case: {ticker}")
        # Note: Binanace might be sensitive to casing if not normalized, but we normalize in adapter.
        df = adapter.get_kline(ticker=ticker, period=period, limit=5, market_type=MarketType.CRYPTO)
        
        self.assertFalse(df.is_empty(), "Should return data for ETH_UsDT")
        self.assertEqual(df[Columns.SYMBOL.value][0], ticker)

    def test_yfinance_stock_usa_mixed_case(self):
        """Test 'AaPL' normalization to 'AAPL'."""
        adapter = YFinanceAdapter()
        ticker = "AaPL"
        period = "1d"
        
        print(f"\n[YFinance Stock] Testing mixed case: {ticker}")
        df = adapter.get_kline(ticker=ticker, period=period, limit=5, market_type=MarketType.STOCK)
        
        self.assertFalse(df.is_empty(), "Should return data for AaPL")
        self.assertEqual(df[Columns.SYMBOL.value][0], ticker)

    def test_akshare_stock_china_numeric(self):
        """Test '000001' (numeric) remains valid."""
        adapter = AKShareAdapter()
        # Numeric case doesn't matter much but ensuring it doesn't break
        ticker = "000001" 
        period = "daily"
        
        print(f"\n[AKShare Stock] Testing numeric: {ticker}")
        df = adapter.get_kline(ticker=ticker, period=period, limit=5, market_type=MarketType.STOCK)
        
        self.assertFalse(df.is_empty(), "Should return data for 000001")
        self.assertEqual(df[Columns.SYMBOL.value][0], ticker)

if __name__ == '__main__':
    unittest.main()
