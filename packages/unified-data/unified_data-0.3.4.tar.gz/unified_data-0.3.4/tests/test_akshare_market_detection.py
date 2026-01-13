
import pytest
from datetime import datetime
from unified_data.adapters.akshare_adapter import AKShareAdapter
from unified_data.models.enums import Market, TimeFramePeriod, MarketType

class TestAKShareMarketDetection:
    
    @pytest.fixture
    def adapter(self):
        return AKShareAdapter()

    def test_detect_market_hk_short(self, adapter):
        # Input '700' -> Should be detected as HK and padded to '00700'
        market, symbol = adapter.detect_market("700")
        assert market == Market.HK
        assert symbol == "00700"

    def test_detect_market_hk_full(self, adapter):
        # Input '00700' -> Should remain '00700' and be HK
        market, symbol = adapter.detect_market("00700")
        assert market == Market.HK
        assert symbol == "00700"

    def test_detect_market_china_a(self, adapter):
        # Input '600519' -> Should be A_SHARE
        market, symbol = adapter.detect_market("600519")
        assert market == Market.A_SHARE
        assert symbol == "600519"

    def test_detect_market_unknown_futures(self, adapter):
        # Input 'RB0' -> Should be UNKNOWN (as it's not a numeric stock code)
        market, symbol = adapter.detect_market("RB0")
        assert market == Market.UNKNOWN
        assert symbol == "RB0"
    
    def test_detect_market_unknown_random(self, adapter):
        # Input 'ABC' 
        market, symbol = adapter.detect_market("ABC")
        assert market == Market.UNKNOWN
        assert symbol == "ABC"

    def test_get_kline_hk_stock(self, adapter):
        # Test live fetch for Tencent (00700)
        # We'll fetch a small amount of data to verify connectivity and parsing
        df = adapter.get_kline(
            ticker="700", 
            period=TimeFramePeriod.D1, 
            limit=5,
            market_type=MarketType.STOCK
        )
        assert not df.is_empty()
        assert "close" in df.columns
        # Verify symbol column has the requested ticker
        assert df["symbol"][0] == "700"

    def test_get_kline_china_stock(self, adapter):
        # Test live fetch for Kweichow Moutai (600519)
        df = adapter.get_kline(
            ticker="600519", 
            period=TimeFramePeriod.D1, 
            limit=5,
            market_type=MarketType.STOCK
        )
        assert not df.is_empty()
        assert "close" in df.columns
