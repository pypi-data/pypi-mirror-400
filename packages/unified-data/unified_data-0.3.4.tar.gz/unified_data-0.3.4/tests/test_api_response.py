import unittest
import polars as pl
from unified_data.api import pull_kline
from unified_data.models.enums import MarketType, Status
from unified_data.models.types import KlineData

class TestApiResponse(unittest.TestCase):
    """
    Test that the API now returns KlineData objects instead of DataFrames.
    """

    def test_stock_success(self):
        """Test getting data for a valid stock."""
        ticker = "AAPL" 
        print(f"\n[Test] Fetching valid stock: {ticker}")
        
        result = pull_kline(ticker, MarketType.STOCK, "1d", limit=10)
        
        self.assertIsInstance(result, KlineData)
        self.assertEqual(result.status, Status.OK)
        self.assertIsInstance(result.data, pl.DataFrame)
        self.assertFalse(result.data.is_empty())
        self.assertEqual(result.error, "")
        
        print("[Test] Success - Status: OK, Data Shape:", result.data.shape)

    def test_invalid_symbol_failure(self):
        """Test reaction to invalid symbols."""
        # Using YF adapter, which previously returned empty DF. Now should be Status.FAILED
        ticker = "INVALID_TICKER_XYZ"
        print(f"\n[Test] Fetching invalid stock: {ticker}")
        
        result = pull_kline(ticker, MarketType.STOCK, "1d")
        
        self.assertIsInstance(result, KlineData)
        self.assertEqual(result.status, Status.FAILED)
        self.assertTrue(result.data.is_empty())
        # "No data returned" or caught exception msg
        print(f"[Test] Failure - Status: {result.status}, Error: {result.error}")
        self.assertNotEqual(result.error, "")

    def test_forced_error(self):
        """Test logic when an exception is raised internally."""
        # CCXT raises exception for bad pair. API should catch and return FAILED.
        ticker = "INVALID/PAIR"
        print(f"\n[Test] Fetching invalid crypto: {ticker}")
        
        result = pull_kline(ticker, MarketType.CRYPTO, "1d")
        
        self.assertIsInstance(result, KlineData)
        self.assertEqual(result.status, Status.FAILED)
        self.assertTrue(result.data.is_empty())
        print(f"[Test] Failure - Status: {result.status}, Error: {result.error}")
        # Check that error contains something meaningful
        self.assertTrue(len(result.error) > 0)

if __name__ == '__main__':
    unittest.main()
