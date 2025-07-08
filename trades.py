
from alpaca.trading.client import TradingClient
from config import get_alpaca_api_key, get_alpaca_secret_key
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce

def market_trade(symbol:str, qty:int=100):
    """
    Submits a market order to buy 100 shares of SOXL.
    Args:
    stock_symbol: str - The stock symbol to trade.
    Returns:
    None
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )

    market_order = trading_client.submit_order(market_order_data)
    print(f"Market order submitted: {market_order}")

def limit_trade(symbol:str, limit_price:float, qty:int=100):
    """
    Submits a limit order to buy 100 shares of SOXL at a specified limit price.
    Args:
    stock_symbol: str - The stock symbol to trade.
    limit_price: float - The price at which to buy the stock.
    qty: int - The number of shares to buy (default is 100).
    Returns:
    None
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    limit_order_data = LimitOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY,
        type=OrderType.MARKET,
        time_in_force=TimeInForce.DAY,
        limit_price=limit_price  # Example limit price, adjust as needed
    )


    limit_order = trading_client.submit_order(limit_order_data)
    print(f"Market order submitted: {limit_order}")