from abc import ABC, abstractmethod
import structlog
import yfinance as yf

logger = structlog.get_logger(__name__)

class MarketProvider(ABC):
    @abstractmethod
    def get_latest_price(self, symbol: str) -> dict:
        pass

class YFinanceProvider(MarketProvider):
    def get_latest_price(self, symbol: str) -> dict:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if hist.empty:
            return None
        latest_price = hist['Close'].iloc[-1]
        return {"price": latest_price, "symbol": symbol}

def get_provider(provider_name: str) -> MarketProvider:
    if provider_name == "yfinance":
        return YFinanceProvider()
    logger.error(
        "Provider not supported", 
        provider=provider_name, 
        exc_info=True
    )
    raise ValueError(f"Provider '{provider_name}' not supported.")