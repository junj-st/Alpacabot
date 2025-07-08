# alpaca bot
from config import get_alpaca_api_key, get_alpaca_secret_key, get_alpaca_api_endpoint
from show_trades import show_trades
from trades import market_trade, limit_trade
from orders import get_orders, cancel_order, getPositions, close_position
# Ensure the .env file is loaded to access environment variables
# This file should be in the same directory as this script or specify the path to it.

