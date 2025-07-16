from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderSide, QueryOrderStatus
from config import get_alpaca_api_key, get_alpaca_secret_key

trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())

def get_orders(limit:int =100):
    """
    Fetches all orders from Alpaca.
    
    Returns:
        list: A list of orders.
    """
    request_params = GetOrdersRequest(
        status=QueryOrderStatus.ALL,
        limit=limit,  # Adjust the limit as needed
    )
    
    orders = trading_client.get_orders(request_params)
    
    for order in orders:
        return (f"Order ID: {order.id}, Symbol: {order.symbol}, Side: {order.side}, Status: {order.status}, Filled Qty: {order.filled_qty}")

def cancel_orders(order_ids:list):
    """
    Cancels an order by its ID.
    
    Args:
        order_id (str): The ID of the order to cancel.
    
    Returns:
        str: Confirmation message of the cancellation.
    """
    trading_client.cancel_orders()
    return f"Order {order_ids} has been cancelled."

def getPositions():
    """
    Fetches all current positions from Alpaca.
    
    Returns:
        list: A list of current positions.
    """
    positions = trading_client.get_all_positions()
    
    for position in positions:
        return (f"Symbol: {position.symbol}, Qty: {position.qty}, Avg Entry Price: {position.avg_entry_price}, Current Price: {position.current_price}")
    

def close_position(symbol):
    """
    Closes a position by its symbol.
    
    Args:
        symbol (str): The symbol of the position to close.
    
    Returns:
        str: Confirmation message of the closure.
    """
    trading_client.close_position(symbol)
    return f"Position for {symbol} has been closed."

def close_all_positions():
    """
    Closes all current positions.
    
    Returns:
        str: Confirmation message of the closure.
    """
    trading_client.close_all_positions()
    return "All positions have been closed."