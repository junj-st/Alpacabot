# alpaca bot
import os

def get_alpaca_api_key():
    """
    Get the Alpaca API key from environment variables.
    """
    api_key = os.getenv('ALPACA_API_KEY')
    if not api_key:
        raise ValueError("ALPACA_API_KEY environment variable is not set.")
    return api_key

