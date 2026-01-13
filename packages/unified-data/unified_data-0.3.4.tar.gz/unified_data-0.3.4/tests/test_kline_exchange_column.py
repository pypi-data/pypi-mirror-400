import sys
import os
import unittest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from unified_data.api import pull_kline
from unified_data.models.enums import MarketType, Exchange, Columns

class TestKlineExchangeColumn(unittest.TestCase):
    """
    Test that the 'exchange' column is correctly added to pull_kline output.
    """

    def test_crypto_exchange_column(self):
        """Test crypto kline has exchange=ccxt column."""
        try:
            res = pull_kline(
                ticker="BTC_USDT",
                market_type=MarketType.CRYPTO,
                period="1d",
                limit=5
            )
            df = res.data
            
            self.assertIn(Columns.EXCHANGE.value, df.columns)
            # Check the value in the first row matches Exchange.CCXT ("ccxt")
            first_exchange = df[Columns.EXCHANGE.value][0]
            self.assertEqual(first_exchange, Exchange.CCXT)
            
        except Exception as e:
            self.fail(f"Crypto exchange column test failed: {e}")

    def test_stock_exchange_column(self):
        """Test stock kline has exchange=yfinance column."""
        try:
            res = pull_kline(
                ticker="AAPL",
                market_type=MarketType.STOCK,
                period="1d",
                limit=5
            )
            df = res.data
            
            self.assertIn(Columns.EXCHANGE.value, df.columns)
            first_exchange = df[Columns.EXCHANGE.value][0]
            self.assertEqual(first_exchange, Exchange.YFINANCE)
            
        except Exception as e:
            self.fail(f"Stock exchange column test failed: {e}")

    def test_explicit_exchange_param(self):
        """Test that explicit exchange parameter is reflected in the column."""
        # Using yfinance for stock explicitly, though it is default
        try:
            res = pull_kline(
                ticker="AAPL",
                market_type=MarketType.STOCK,
                period="1d",
                limit=5,
                exchange=Exchange.YFINANCE
            )
            df = res.data
            
            self.assertIn(Columns.EXCHANGE.value, df.columns)
            self.assertEqual(df[Columns.EXCHANGE.value][0], Exchange.YFINANCE)
            
        except Exception as e:
            self.fail(f"Explicit exchange param test failed: {e}")

if __name__ == '__main__':
    unittest.main()
