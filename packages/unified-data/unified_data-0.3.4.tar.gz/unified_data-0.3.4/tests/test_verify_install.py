import unittest
from unified_data import pull_kline, MarketType

class TestInstalledPackage(unittest.TestCase):
    def test_live_pull(self):
        print("\n[Verification] Attempting to pull BTC_USDT from installed package...")
        try:
            res = pull_kline("BTC_USDT", MarketType.CRYPTO, "1d", limit=1)
            df = res.data
            print(f"[Verification] Success! Fetched {len(df)} rows.")
            print(df)
            self.assertFalse(df.is_empty())
        except Exception as e:
            self.fail(f"Detailed failure: {e}")

if __name__ == '__main__':
    unittest.main()
