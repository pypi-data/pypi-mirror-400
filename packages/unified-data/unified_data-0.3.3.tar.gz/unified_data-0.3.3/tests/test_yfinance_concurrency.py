
import sys
import os
import unittest
import polars as pl
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from unified_data.adapters.yfinance_adapter import YFinanceAdapter
from unified_data.models.enums import Columns

class TestYFinanceConcurrency(unittest.TestCase):
    def setUp(self):
        self.adapter = YFinanceAdapter()
        self.tickers = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"]

    def fetch_data(self, ticker):
        """Helper to fetch data and return result or error."""
        try:
            # Short limit to be fast
            df = self.adapter.get_kline(ticker, "1d", limit=5)
            return ticker, df, None
        except Exception as e:
            return ticker, None, e

    def test_concurrent_fetching(self):
        """Test fetching data for multiple tickers concurrently."""
        print(f"\n[Concurrency] Starting fetch for {len(self.tickers)} tickers...")
        
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_ticker = {executor.submit(self.fetch_data, t): t for t in self.tickers}
            
            for future in as_completed(future_to_ticker):
                results.append(future.result())

        for ticker, df, error in results:
            with self.subTest(ticker=ticker):
                if error:
                    self.fail(f"Failed to fetch {ticker}: {error}")
                
                # Verify DataFrame structure
                self.assertIsInstance(df, pl.DataFrame)
                self.assertFalse(df.is_empty(), f"DataFrame for {ticker} is empty")
                self.assertEqual(len(df), 5, f"Expected 5 rows for {ticker}, got {len(df)}")
                
                # Verify Columns (Critical Check for MultiIndex issues)
                expected_cols = [
                    Columns.TIMESTAMP.value, 
                    Columns.OPEN.value, 
                    Columns.HIGH.value, 
                    Columns.LOW.value, 
                    Columns.CLOSE.value, 
                    Columns.VOLUME.value
                ]
                
                print(f"[Concurrency] {ticker} checked. Columns: {df.columns}")
                
                for col in expected_cols:
                    self.assertIn(col, df.columns, f"Missing column {col} in {ticker}")
                    
                # Verify no tuple columns (MultiIndex artifact)
                for col_name in df.columns:
                    self.assertNotIsInstance(col_name, tuple, f"Column {col_name} is a tuple! MultiIndex detected.")

if __name__ == "__main__":
    unittest.main()
