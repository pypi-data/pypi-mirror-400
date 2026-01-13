import sys
import os
import unittest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

class TestTopLevelImports(unittest.TestCase):
    """
    Verify that main API components can be imported from the top-level package.
    """

    def test_top_level_imports(self):
        try:
            from unified_data import pull_kline, MarketType, Exchange, Columns, TimeFramePeriod
            self.assertTrue(callable(pull_kline))
            self.assertEqual(MarketType.CRYPTO, "crypto")
            self.assertEqual(Exchange.BINANCE, "binance")
            self.assertEqual(Columns.TIMESTAMP, "ts")
            self.assertEqual(TimeFramePeriod.D1, "1d")
            print("\n[Top-Level Import Test] All imports successful!")
        except ImportError as e:
            self.fail(f"Top-level import failed: {e}")

if __name__ == "__main__":
    unittest.main()
