import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from config import get_alpaca_api_key, get_alpaca_secret_key
from ta.momentum import RSIIndicator
from datetime import datetime, timedelta

def get_rsi(symbol: str, period: int = 14, latest_only: bool = False):
    """
    Fetches RSI data for a given stock symbol using Alpaca's historical bars.
    """
    try:
        client = StockHistoricalDataClient(get_alpaca_api_key(), get_alpaca_secret_key())
        end = datetime.utcnow()
        start = end - timedelta(days=10)

        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            start=start.isoformat() + "Z",
            end=end.isoformat() + "Z",
            timeframe=TimeFrame.Minute
        )
        bars = client.get_stock_bars(request).df

        if bars.empty:
            return None

        # Filter for just this symbol if multi-symbol returned
        if symbol not in bars.index.get_level_values(0):
            return None

        bars = bars.loc[symbol].reset_index()
        if 'close' not in bars.columns or len(bars) < period + 1:
            return None

        bars['rsi'] = RSIIndicator(bars['close'], window=period).rsi()

        if latest_only:
            latest_rsi = bars['rsi'].iloc[-1]
            return round(latest_rsi, 2) if pd.notna(latest_rsi) else None

        return bars

    except Exception as e:
        print(f"[ERROR] Failed to fetch RSI for {symbol}: {e}")
        return None
