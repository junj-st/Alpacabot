from marketdata import get_latest_price
from trades import (
    percent_market_buy,
    market_sell,
    get_position_qty,
    percent_market_buy_crypto,
    market_sell_crypto,
    get_crypto_position_qty,
)
from rsi import get_rsi
import time
from datetime import datetime, timedelta
import pytz

# === Strategy Parameters ===
TICKERS = [
    'ORCL', 'WBD', 'NVDL',
    'MRVL', 'AFRM', 'SOXL', 'CCL', 'OKTA', 'PTON', 'PLTR', 'WDC', 'QS'
]
RSI_LENGTH = 14
OVERSOLD = 20
OVERBOUGHT = 80
STOP_LOSS_PCT = 2.5
TAKE_PROFIT_PCT = 1.0
TRADE_PERCENTAGE = 1.5  # 150% per position
MAX_POSITIONS = 2  # Matches 50% per position
CHECK_INTERVAL = 1.0  # seconds

# === Position Tracking per Ticker ===
positions = {symbol: {"open": False, "entry_price": None, "entry_time": None, "qty": 0} for symbol in TICKERS}

def count_open_positions():
    return sum(1 for symbol in positions if positions[symbol]["open"])

def is_market_open():
    """Check if US market is currently open, excluding first 30 min and last 15 min."""
    eastern = pytz.timezone("US/Eastern")
    now_eastern = datetime.now(eastern)
    
    # Check if weekend
    if now_eastern.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Market hours (9:30 AM - 4:00 PM ET)
    market_open = now_eastern.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_eastern.replace(hour=16, minute=0, second=0, microsecond=0)
    # Restrict first 30 min and last 15 min
    restricted_start = now_eastern.replace(hour=10, minute=0, second=0, microsecond=0)
    restricted_end = now_eastern.replace(hour=15, minute=45, second=0, microsecond=0)
    return restricted_start <= now_eastern < restricted_end

def close_all_positions():
    """Close all open positions at end of day"""
    for symbol in TICKERS:
        if positions[symbol]["open"]:
            print(f"End of day: Closing position in {symbol}")
            result = market_sell(symbol)
            if result:
                positions[symbol] = {"open": False, "entry_price": None, "entry_time": None, "qty": 0}

def sync_positions():
    """Sync our position tracking with actual Alpaca positions"""
    for symbol in TICKERS:
        actual_qty = get_position_qty(symbol)
        if actual_qty > 0 and not positions[symbol]["open"]:
            # We have shares but our tracker says we don't
            print(f"Found untracked position in {symbol}: {actual_qty} shares")
            positions[symbol]["open"] = True
            positions[symbol]["qty"] = actual_qty
            # We don't know the entry price, so we'll use current price
            positions[symbol]["entry_price"] = get_latest_price(symbol)
        elif actual_qty == 0 and positions[symbol]["open"]:
            # Our tracker says we have shares but we don't
            print(f"Position in {symbol} was closed externally")
            positions[symbol] = {"open": False, "entry_price": None, "entry_time": None, "qty": 0}

# === Crypto Strategy Parameters ===
CRYPTO_TICKERS = ['LINK/USD', 'ETH/USD', 'BCH/USD', 'AAVE/USD']
CRYPTO_RSI_LENGTH = 14
CRYPTO_RSI_BUY = 14
CRYPTO_TRADE_PERCENTAGE = 1.0  # 100% per position
CRYPTO_MAX_POSITIONS = 1

# === Position Tracking per Crypto Ticker ===
crypto_positions = {symbol: {"open": False, "entry_price": None, "entry_time": None, "qty": 0} for symbol in CRYPTO_TICKERS}

def count_open_crypto_positions():
    return sum(1 for symbol in crypto_positions if crypto_positions[symbol]["open"])

def get_crypto_trade_window_and_params(now_eastern):
    weekday = now_eastern.weekday()  # Monday=0, Sunday=6
    hour = now_eastern.hour
    minute = now_eastern.minute

    # Weekend window: Friday 4:30 PM to Monday 8 AM
    friday_window_start = now_eastern.replace(hour=16, minute=30, second=0, microsecond=0)
    monday_window_end = now_eastern.replace(hour=8, minute=0, second=0, microsecond=0)
    if (
        (weekday == 4 and (hour > 16 or (hour == 16 and minute >= 30))) or  # Friday after 4:30 PM
        (weekday == 5) or  # Saturday
        (weekday == 6) or  # Sunday
        (weekday == 0 and (hour < 8))  # Monday before 8 AM
    ):
        # Weekend trading window
        return True, 1.0, 2.0  # Stop Loss 1%, Take Profit 2%

    # Weekday windows
    if 17 <= hour or hour < 4:  # 5 PM to 4 AM
        return True, 1.0, 2.0  # Stop Loss 1%, Take Profit 2%
    elif 4 <= hour < 9 or (hour == 9 and minute < 30):  # 4 AM to 9:30 AM
        return True, 1.0, 2.0  # Stop Loss 1%, Take Profit 2%
    else:
        return False, None, None  # Not in trading window

# === Main Bot Loop ===
print("Starting RSI Trading Bot...")

while True:
    try:
        eastern = pytz.timezone("US/Eastern")
        now_eastern = datetime.now(eastern)
        current_time_str = now_eastern.strftime("%Y-%m-%d %H:%M")
        
        # Check if market is open (excluding first 30 min and last 15 min)
        if not is_market_open():
            # At 15:45 (3:45 PM ET), close all positions
            if now_eastern.hour == 15 and now_eastern.minute == 45:
                print("Market close approaching: Closing all positions.")
                close_all_positions()
            print(f"Market closed or restricted at {current_time_str}. Waiting...")
            time.sleep(CHECK_INTERVAL)
            continue
        
        # Sync positions every iteration
        sync_positions()
        
        for symbol in TICKERS:
            try:
                df = get_rsi(symbol, RSI_LENGTH)
                if (
                    df is None
                    or 'rsi' not in df.columns
                    or df['rsi'].isna().iloc[-1]
                    or len(df) < 2
                ):
                    continue

                rsi_now = df['rsi'].iloc[-1]
                rsi_prev = df['rsi'].iloc[-2]
                latest_price = get_latest_price(symbol)
                
                if latest_price is None:
                    print(f"[WARN] No price for {symbol}, skipping.")
                    continue

                # === Exit Signal (TP/SL/Overbought) ===
                if positions[symbol]["open"]:
                    entry = positions[symbol]["entry_price"]
                    if entry is None or entry == 0:
                        print(f"[WARN] Invalid entry price for {symbol}, skipping exit check.")
                        continue
                    
                    change_pct = (latest_price - entry) / entry * 100

                    # Take Profit
                    if change_pct >= TAKE_PROFIT_PCT:
                        print(f"{symbol}: Take Profit hit (+{change_pct:.2f}%). Selling...")
                        result = market_sell(symbol)
                        if result:
                            positions[symbol] = {"open": False, "entry_price": None, "entry_time": None, "qty": 0}
                        continue

                    # Stop Loss
                    elif change_pct <= -STOP_LOSS_PCT:
                        print(f"{symbol}: Stop Loss hit ({change_pct:.2f}%). Selling...")
                        result = market_sell(symbol)
                        if result:
                            positions[symbol] = {"open": False, "entry_price": None, "entry_time": None, "qty": 0}
                        continue
                    
                    # Overbought Exit
                    elif rsi_now >= OVERBOUGHT:
                        print(f"{symbol}: RSI overbought ({rsi_now:.2f}). Selling...")
                        result = market_sell(symbol)
                        if result:
                            positions[symbol] = {"open": False, "entry_price": None, "entry_time": None, "qty": 0}
                        continue

                print(f"{symbol}: rsi_prev={rsi_prev}, rsi_now={rsi_now}, open={positions[symbol]['open']}, open_positions={count_open_positions()}")

                # === Entry Signal ===
                if (not positions[symbol]["open"] and 
                    rsi_prev < OVERSOLD and 
                    rsi_now >= OVERSOLD and
                    count_open_positions() < MAX_POSITIONS):
                    
                    print(f"{symbol}: RSI crossed above {OVERSOLD} ({rsi_now:.2f}). Buying...")
                    order = percent_market_buy(symbol, TRADE_PERCENTAGE)
                    
                    if order:
                        # Try to get fill price from order
                        try:
                            actual_entry_price = float(order.filled_avg_price) if hasattr(order, 'filled_avg_price') and order.filled_avg_price else latest_price
                            actual_qty = int(float(order.filled_qty)) if hasattr(order, 'filled_qty') and order.filled_qty else 0
                        except:
                            actual_entry_price = latest_price
                            actual_qty = 0
                        
                        print(f"Order executed: {order}")
                        positions[symbol]["open"] = True
                        positions[symbol]["entry_price"] = actual_entry_price
                        positions[symbol]["entry_time"] = now_eastern
                        positions[symbol]["qty"] = actual_qty
                    continue

                # Status update
                if positions[symbol]["open"]:
                    entry = positions[symbol]["entry_price"]
                    entry_str = f"${entry:.2f}" if entry else "N/A"
                    change_pct = (latest_price - entry) / entry * 100 if entry else 0
                    print(f"{symbol}: RSI={rsi_now:.2f}, Price=${latest_price:.2f}, Entry={entry_str}, P&L={change_pct:+.2f}%, Qty={positions[symbol]['qty']}, Time={current_time_str}")
                else:
                    print(f"{symbol}: RSI={rsi_now:.2f}, Price=${latest_price:.2f}, No Position, Time={current_time_str}")

            except Exception as stock_error:
                print(f"[ERROR] Failed for {symbol}: {stock_error}")

        print(f"Open positions: {count_open_positions()}/{MAX_POSITIONS}")
        print("-" * 50)

        # --- Crypto Trading Logic ---
        crypto_trading, stop_loss_pct, take_profit_pct = get_crypto_trade_window_and_params(now_eastern)
        if crypto_trading:
            for symbol in CRYPTO_TICKERS:
                try:
                    df = get_rsi(symbol, CRYPTO_RSI_LENGTH)
                    if (
                        df is None
                        or 'rsi' not in df.columns
                        or df['rsi'].isna().iloc[-1]
                        or len(df) < 2
                    ):
                        continue

                    rsi_now = df['rsi'].iloc[-1]
                    rsi_prev = df['rsi'].iloc[-2]
                    latest_price = get_latest_price(symbol)

                    if latest_price is None:
                        print(f"[CRYPTO][WARN] No price for {symbol}, skipping.")
                        continue

                    # === Exit Signal (TP/SL) ===
                    if crypto_positions[symbol]["open"]:
                        entry = crypto_positions[symbol]["entry_price"]
                        if entry is None or entry == 0:
                            print(f"[CRYPTO][WARN] Invalid entry price for {symbol}, skipping exit check.")
                            continue

                        change_pct = (latest_price - entry) / entry * 100

                        # Take Profit
                        if change_pct >= take_profit_pct:
                            print(f"[CRYPTO]{symbol}: Take Profit hit (+{change_pct:.2f}%). Selling...")
                            result = market_sell_crypto(symbol)
                            if result:
                                crypto_positions[symbol] = {"open": False, "entry_price": None, "entry_time": None, "qty": 0}
                            continue

                        # Stop Loss
                        elif change_pct <= -stop_loss_pct:
                            print(f"[CRYPTO]{symbol}: Stop Loss hit ({change_pct:.2f}%). Selling...")
                            result = market_sell_crypto(symbol)
                            if result:
                                crypto_positions[symbol] = {"open": False, "entry_price": None, "entry_time": None, "qty": 0}
                            continue

                    # === Entry Signal ===
                    if (
                        not crypto_positions[symbol]["open"]
                        and rsi_prev < CRYPTO_RSI_BUY
                        and rsi_now >= CRYPTO_RSI_BUY
                        and count_open_crypto_positions() < CRYPTO_MAX_POSITIONS
                    ):
                        print(f"[CRYPTO]{symbol}: RSI crossed above {CRYPTO_RSI_BUY} ({rsi_now:.2f}). Buying...")
                        order = percent_market_buy_crypto(symbol, CRYPTO_TRADE_PERCENTAGE)
                        if order:
                            try:
                                actual_entry_price = float(order.filled_avg_price) if hasattr(order, 'filled_avg_price') and order.filled_avg_price else latest_price
                                actual_qty = float(order.filled_qty) if hasattr(order, 'filled_qty') and order.filled_qty else 0
                            except Exception:
                                actual_entry_price = latest_price
                                actual_qty = 0
                            print(f"[CRYPTO] Order executed: {order}")
                            crypto_positions[symbol]["open"] = True
                            crypto_positions[symbol]["entry_price"] = actual_entry_price
                            crypto_positions[symbol]["entry_time"] = now_eastern
                            crypto_positions[symbol]["qty"] = actual_qty
                        continue

                    # Status update
                    if crypto_positions[symbol]["open"]:
                        entry = crypto_positions[symbol]["entry_price"]
                        entry_str = f"${entry:.2f}" if entry else "N/A"
                        change_pct = (latest_price - entry) / entry * 100 if entry else 0
                        print(f"[CRYPTO]{symbol}: RSI={rsi_now:.2f}, Price=${latest_price:.2f}, Entry={entry_str}, P&L={change_pct:+.2f}%, Qty={crypto_positions[symbol]['qty']}, Time={current_time_str}")
                    else:
                        print(f"[CRYPTO]{symbol}: RSI={rsi_now:.2f}, Price=${latest_price:.2f}, No Position, Time={current_time_str}")

                except Exception as crypto_error:
                    print(f"[CRYPTO][ERROR] Failed for {symbol}: {crypto_error}")

            print(f"[CRYPTO] Open positions: {count_open_crypto_positions()}/{CRYPTO_MAX_POSITIONS}")
            print("-" * 50)

    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")

    time.sleep(CHECK_INTERVAL)