from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from config import get_alpaca_api_key, get_alpaca_secret_key
# keys required for stock historical data client
def get_latest_price(symbol: str) -> float:
    """    Fetches the latest price for a given stock symbol.  
    Args:
        symbol (str): The stock symbol to fetch the latest price for.
    Returns:
        float: The latest price of the stock.
    """ 
    client = StockHistoricalDataClient(get_alpaca_api_key(), get_alpaca_secret_key())

        # multi symbol request - single symbol is similar
    multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=symbol)

    latest_multisymbol_quotes = client.get_stock_latest_quote(multisymbol_request_params)
    latest_bid_price = latest_multisymbol_quotes[symbol].bid_price

    return latest_bid_price