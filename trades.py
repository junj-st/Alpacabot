from alpaca.trading.client import TradingClient
from config import get_alpaca_api_key, get_alpaca_secret_key
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce
from percentage import getPortfolio_value, getEstimate_value, getCash_value
from datetime import datetime
from show_trades import show_trades
from marketdata import get_latest_price


def market_buy(symbol:str, qty:int=100):
    """
    Submits a market order to buy 100 shares of a stock.
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
    
    return market_order


def limit_buy(symbol:str, limit_price:float, qty:int=100):
    """
    Submits a limit order to buy 100 shares of a stock at a specified limit price.
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


def percent_market_buy(symbol:str, percentage:float):
    """
    Submits a market order to buy a percentage of the portfolio value in a stock.
    Args:
    stock_symbol: str - The stock symbol to trade.
    percentage: float - The percentage of the portfolio value to use for the trade.
    Returns:
    None
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    portfolio_value = getPortfolio_value()
    estimate_value = getEstimate_value(percentage)
    if(estimate_value > getCash_value()):
        print("Not enough cash to perform this trade.")
        return
    lastPrice = get_latest_price(symbol)
    qty = int(estimate_value / lastPrice)
    
    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )

    market_order = trading_client.submit_order(market_order_data)
    
    return market_order


def percent_limit_buy(symbol:str, limit_price:float, percentage:float):
    """
    Submits a limit order to buy a percentage of the portfolio value in a stock at a specified limit price.
    Args:       
    stock_symbol: str - The stock symbol to trade.
    limit_price: float - The price at which to buy the stock.
    percentage: float - The percentage of the portfolio value to use for the trade.
    Returns:
    None
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    portfolio_value = getPortfolio_value()
    estimate_value = getEstimate_value(percentage)
    if(estimate_value > getCash_value()):
        print("Not enough cash to perform this trade.")
        return
    qty = int(estimate_value / limit_price)
    
    limit_order_data = LimitOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        time_in_force=TimeInForce.DAY,
        limit_price=limit_price
    )

    limit_order = trading_client.submit_order(limit_order_data)
    
    return(f"Limit order submitted: {limit_order}")

def market_sell(symbol: str, qty: int = None):
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())

    if qty is None:
        qty = get_position_qty(symbol)
        if qty == 0:
            print(f"[INFO] No shares to sell for {symbol}")
            return None

    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.DAY
    )

    market_order = trading_client.submit_order(market_order_data)
    print(f"Market order submitted: {market_order}")
    return market_order

def limit_sell(symbol:str, limit_price:float, qty:int=100): 
    """
    Submits a limit order to sell 100 shares of a stock at a specified limit price.
    Args:
    stock_symbol: str - The stock symbol to trade.
    limit_price: float - The price at which to sell the stock.
    qty: int - The number of shares to sell (default is 100).
    Returns:
    None
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    limit_order_data = LimitOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.SELL,
        type=OrderType.LIMIT,
        time_in_force=TimeInForce.DAY,
        limit_price=limit_price  # Example limit price, adjust as needed
    )

    limit_order = trading_client.submit_order(limit_order_data)
    
    print(f"Limit order submitted: {limit_order}")

def percent_market_sell(symbol:str, percentage:float):
    """
    Submits a market order to sell a percentage of the portfolio value in a stock.
    Args:
    stock_symbol: str - The stock symbol to trade.
    percentage: float - The percentage of the portfolio value to use for the trade.
    Returns:
    None
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    portfolio_value = getPortfolio_value()
    estimate_value = getEstimate_value(percentage)
    
    lastPrice = get_latest_price(symbol)
    qty = int(estimate_value / lastPrice)
    
    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.DAY
    )

    market_order = trading_client.submit_order(market_order_data)
    
    return market_order


def percent_limit_sell(symbol:str, limit_price:float, percentage:float):
    """
    Submits a limit order to sell a percentage of the portfolio value in a stock at a specified limit price.
    Args:  
    stock_symbol: str - The stock symbol to trade.
    limit_price: float - The price at which to sell the stock.
    percentage: float - The percentage of the portfolio value to use for the trade.
    Returns:
    None       
    """                             
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    portfolio_value = getPortfolio_value()
    estimate_value = getEstimate_value(percentage)
    
    qty = int(estimate_value / limit_price)
    
    limit_order_data = LimitOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.SELL,
        type=OrderType.LIMIT,
        time_in_force=TimeInForce.DAY,
        limit_price=limit_price
    )

    limit_order = trading_client.submit_order(limit_order_data)
    
    return(f"Limit order submitted: {limit_order}")

def get_position_qty(symbol: str) -> int:
    """
    Returns the quantity of shares held for the given symbol.
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    try:
        position = trading_client.get_open_position(symbol)
        return int(float(position.qty))
    except Exception:
        # No position or error
        return 0

def market_buy_crypto(symbol: str, qty: float = 0.01):
    """
    Submits a market order to buy a quantity of a crypto asset.
    Args:
        symbol: str - The crypto symbol to trade (e.g., 'BTC/USD').
        qty: float - The quantity to buy.
    Returns:
        The order object.
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.GTC  # Crypto trades are GTC
    )
    market_order = trading_client.submit_order(market_order_data)
    return market_order

def market_sell_crypto(symbol: str, qty: float = None):
    """
    Submits a market order to sell a quantity of a crypto asset.
    Args:
        symbol: str - The crypto symbol to trade (e.g., 'BTC/USD').
        qty: float - The quantity to sell. If None, sells entire position.
    Returns:
        The order object.
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    if qty is None:
        qty = get_crypto_position_qty(symbol)
        if qty == 0:
            print(f"[INFO] No crypto to sell for {symbol}")
            return None
    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.GTC
    )
    market_order = trading_client.submit_order(market_order_data)
    return market_order

def percent_market_buy_crypto(symbol: str, percentage: float):
    """
    Submits a market order to buy a percentage of the portfolio value in a crypto asset.
    Args:
        symbol: str - The crypto symbol to trade (e.g., 'BTC/USD').
        percentage: float - The percentage of the portfolio value to use for the trade.
    Returns:
        The order object.
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    portfolio_value = getPortfolio_value()
    estimate_value = getEstimate_value(percentage)
    if estimate_value > getCash_value():
        print("Not enough cash to perform this crypto trade.")
        return
    lastPrice = get_latest_price(symbol)
    qty = estimate_value / lastPrice
    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.GTC
    )
    market_order = trading_client.submit_order(market_order_data)
    return market_order

def percent_market_sell_crypto(symbol: str, percentage: float):
    """
    Submits a market order to sell a percentage of the portfolio value in a crypto asset.
    Args:
        symbol: str - The crypto symbol to trade (e.g., 'BTC/USD').
        percentage: float - The percentage of the portfolio value to use for the trade.
    Returns:
        The order object.
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    portfolio_value = getPortfolio_value()
    estimate_value = getEstimate_value(percentage)
    lastPrice = get_latest_price(symbol)
    qty = estimate_value / lastPrice
    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.GTC
    )
    market_order = trading_client.submit_order(market_order_data)
    return market_order

def get_crypto_position_qty(symbol: str) -> float:
    """
    Returns the quantity of crypto held for the given symbol.
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    try:
        position = trading_client.get_open_position(symbol)
        return float(position.qty)
    except Exception:
        # No position or error
        return 0.0