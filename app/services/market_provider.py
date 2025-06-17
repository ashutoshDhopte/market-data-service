from abc import ABC, abstractmethod
import yfinance as yf

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
    raise ValueError(f"Provider '{provider_name}' not supported.")