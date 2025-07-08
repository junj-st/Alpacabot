
from alpaca.trading.client import TradingClient
from alpaca.data import StockHistoricalDataClient, StockTradesRequest
from config import get_alpaca_api_key, get_alpaca_secret_key
from datetime import datetime

def show_trades(stock_symbol:str,start_time: str, end_time:str):
    """"
    args:
    stock_symbol: str - The stock symbol to fetch trades for
    start_time: str - Start time in the format "YYYY-MM-DD HH:MM"
    end_time: str - End time in the format "YYYY-MM-DD HH:MM"   

    Returns:
    trades: list - List of trades within the specified time range
    """
    request_params = StockTradesRequest(
        symbol_or_symbols=stock_symbol,
        start=datetime.strptime(start_time, "%Y-%m-%d %H:%M"),
        end=datetime.strptime(end_time, "%Y-%m-%d %H:%M"),
    )
    data_client = StockHistoricalDataClient(get_alpaca_api_key(), get_alpaca_secret_key())

    trades = data_client.get_stock_trades(request_params)

    return trades