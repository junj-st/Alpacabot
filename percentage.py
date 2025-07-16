from alpaca.trading.client import TradingClient
from config import get_alpaca_api_key, get_alpaca_secret_key

def getPortfolio_value():
    """
    Fetches the current portfolio value from Alpaca.
    
    Returns:
        float: The current portfolio value.
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    account = trading_client.get_account()
    
    return float(account.portfolio_value) if account else 0.0

def getEstimate_value(percentage: float):
    """
    Estimates the portfolio value based on a given percentage.
    
    Args:
        percentage (float): The percentage of the portfolio to estimate.
        
    Returns:
        float: The estimated portfolio value.
    """
    current_value = getPortfolio_value()
    return current_value * (percentage) if current_value else 0.0

def getCash_value():
    """
    Fetches the current cash value from Alpaca.
    
    Returns:
        float: The current cash value.
    """
    trading_client = TradingClient(get_alpaca_api_key(), get_alpaca_secret_key())
    account = trading_client.get_account()
    
    return float(account.cash) if account else 0.0
    