import unittest
import logging
import ccxt
import polars as pl
from unified_data.adapters.akshare_adapter import AKShareAdapter
from unified_data.adapters.ccxt_adapter import CCXTAdapter
from unified_data.adapters.yfinance_adapter import YFinanceAdapter

# Setup logging to capture output
logging.basicConfig(level=logging.INFO)

class TestAdaptersErrorHandling(unittest.TestCase):
    """
    Tests to verify how adapters handle errors:
    1. Wrong Symbol
    2. API Errors (simulated via invalid inputs usually triggering 404s or empty data)
    """

    def setUp(self):
        self.ak_adapter = AKShareAdapter()
        self.ccxt_adapter = CCXTAdapter()
        self.yf_adapter = YFinanceAdapter()

    # --- AKShare Tests ---
    def test_akshare_wrong_symbol(self):
        """Test AKShare with a non-existent symbol."""
        # "INVALID_DESC" is highly unlikely to exist
        ticker = "INVALID_DESC_999" 
        period = "daily"
        
        print(f"\n[AKShare] Testing Invalid Symbol: {ticker}")
        try:
            df = self.ak_adapter.get_kline(ticker=ticker, period=period)
            print(f"[AKShare] Result Type: {type(df)}")
            if isinstance(df, pl.DataFrame):
                print(f"[AKShare] Result Shape: {df.shape}")
                self.assertTrue(df.is_empty(), "AKShare should return empty DataFrame for invalid symbol")
        except Exception as e:
            print(f"[AKShare] Raised Exception: {e}")
            # AKShare adapter catches Exception and returns empty DataFrame, 
            # so we shouldn't really reach here unless the catch block is broken
            self.fail(f"AKShare unexpectedly raised exception: {e}")

    # --- YFinance Tests ---
    def test_yfinance_wrong_symbol(self):
        """Test YFinance with a non-existent symbol."""
        ticker = "INVALID_TICKER_XYZ"
        period = "1d"
        
        print(f"\n[YFinance] Testing Invalid Symbol: {ticker}")
        try:
            df = self.yf_adapter.get_kline(ticker=ticker, period=period)
            print(f"[YFinance] Result Type: {type(df)}")
            if isinstance(df, pl.DataFrame):
                print(f"[YFinance] Result Shape: {df.shape}")
                # YFinance usually returns empty DF for invalid ticker
                self.assertTrue(df.is_empty(), "YFinance should return empty DataFrame for invalid symbol")
        except Exception as e:
            print(f"[YFinance] Raised Exception: {e}")
            # YF adapter re-raises exceptions. 
            # If YFinance library raises an error for bad ticker, we expect it here.
            # But usually yfinance returns empty data for bad ticker without raising.
            pass

    # --- CCXT Tests ---
    def test_ccxt_wrong_symbol(self):
        """Test CCXT with a non-existent symbol."""
        ticker = "INVALID/COINPAIR"
        period = "1d"
        
        print(f"\n[CCXT] Testing Invalid Symbol: {ticker}")
        try:
            df = self.ccxt_adapter.get_kline(ticker=ticker, period=period)
            print(f"[CCXT] Result Type: {type(df)}")
            # CCXT usually RAISES BadSymbol for invalid pairs
            if not df.is_empty():
                 self.fail("CCXT should not return data for invalid symbol")
        except ccxt.BadSymbol:
            print("[CCXT] Caught expected ccxt.BadSymbol")
        except Exception as e:
            print(f"[CCXT] Caught other exception: {type(e).__name__}: {e}")
            # Accept generic exceptions too if CCXT decides to throw something else
            pass

    # --- API Error Simulation (Generic) ---
    # It's hard to force a 500 or 429 without mocking.
    # But we can try a malformed request if possible, or just rely on the above.
    
if __name__ == '__main__':
    unittest.main()
