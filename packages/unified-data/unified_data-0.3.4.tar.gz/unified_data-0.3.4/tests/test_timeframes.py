
import pytest
from datetime import datetime
from unified_data.adapters.ccxt_adapter import CCXTAdapter
from unified_data.adapters.yfinance_adapter import YFinanceAdapter
from unified_data.adapters.akshare_adapter import AKShareAdapter
from unified_data.models.enums import TimeFramePeriod, MarketType

class TestTimeFrames:

    def test_ccxt_conversion(self):
        adapter = CCXTAdapter()
        assert adapter.to_exchange_period("1d") == "1d"
        assert adapter.to_exchange_period("1w") == "1w"
        assert adapter.to_exchange_period("1M") == "1M"
        assert adapter.to_exchange_period(TimeFramePeriod.D1) == "1d"
        assert adapter.to_exchange_period(TimeFramePeriod.M1) == "1M"

    def test_yfinance_conversion(self):
        adapter = YFinanceAdapter()
        assert adapter.to_exchange_period("1d") == "1d"
        assert adapter.to_exchange_period("1w") == "1wk"
        assert adapter.to_exchange_period("1M") == "1mo"
        assert adapter.to_exchange_period(TimeFramePeriod.D1) == "1d"
        assert adapter.to_exchange_period(TimeFramePeriod.M1) == "1mo"

    def test_akshare_conversion(self):
        adapter = AKShareAdapter()
        assert adapter.to_exchange_period("1d") == "daily"
        assert adapter.to_exchange_period("1w") == "weekly"
        assert adapter.to_exchange_period("1M") == "monthly"
        assert adapter.to_exchange_period(TimeFramePeriod.D1) == "daily"
        assert adapter.to_exchange_period(TimeFramePeriod.M1) == "monthly"

    @pytest.mark.integration
    def test_ccxt_fetch(self):
        adapter = CCXTAdapter()
        # BTC/USDT is standard
        # Try 1w to verify
        df = adapter.get_kline("BTC_USDT", "1w", limit=5)
        assert not df.is_empty()
        assert len(df) <= 5

    @pytest.mark.integration
    def test_yfinance_fetch(self):
        adapter = YFinanceAdapter()
        # AAPL
        # Try 1M (Monthly) which maps to "1mo"
        df = adapter.get_kline("AAPL", "1M", limit=5, market_type=MarketType.STOCK)
        assert not df.is_empty()
        assert len(df) <= 5

    @pytest.mark.integration
    def test_akshare_fetch(self):
        adapter = AKShareAdapter()
        # 000001 (Ping An)
        # Try 1w (weekly)
        df = adapter.get_kline("000001", "1w", limit=5, market_type=MarketType.STOCK)
        assert not df.is_empty()
        assert len(df) <= 5
