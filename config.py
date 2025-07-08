from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()



def get_alpaca_api_key():
    """
    Get the Alpaca API key from environment variables.
    """
    api_key = os.getenv('ALPACA_API_KEY')
    if not api_key:
        raise ValueError("ALPACA_API_KEY environment variable is not set.")
    return api_key

def get_alpaca_secret_key():
    """
    Get the Alpaca secret key from environment variables.
    """
    secret_key = os.getenv('ALPACA_API_SECRET')
    if not secret_key:
        raise ValueError("ALPACA_API_SECRET environment variable is not set.")
    return secret_key

def get_alpaca_api_endpoint():
    """
    Get the Alpaca API endpoint from environment variables.
    """
    api_endpoint = os.getenv('ALPACA_API_ENDPOINT')
    if not api_endpoint:
        raise ValueError("ALPACA_API_ENDPOINT environment variable is not set.")
    return api_endpoint

def get_alpaca_both_keys():
    """
    Get both the Alpaca API key and secret key.
    
    Returns:
        tuple: A tuple containing the API key and secret key.
    """
    return get_alpaca_api_key(), get_alpaca_secret_key()