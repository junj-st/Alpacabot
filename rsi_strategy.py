from marketdata import get_latest_price
from trades import percent_market_buy, market_sell, get_position_qty
from rsi import get_rsi
import time
from datetime import datetime
import pytz

# === Strategy Parameters ===
TICKERS = [
    'ORCL', 'MRNA', 'WBD', 'BA', 'NVDL', 'RTX',
    'MRVL', 'AMAT', 'TXN', 'IBM', 'HIMS', 'AFRM', 'SOXL', 'LUV', 'TFC', 'CCL'
]
RSI_LENGTH = 14
OVERSOLD = 20
OVERBOUGHT = 80
STOP_LOSS_PCT = 2.5
TAKE_PROFIT_PCT = 1.0
TRADE_PERCENTAGE = 0.33  # 33% per position
MAX_POSITIONS = 3  # Matches 33% per position
CHECK_INTERVAL = 0.5  # seconds

# === Position Tracking per Ticker ===
positions = {symbol: {"open": False, "entry_price": None, "entry_time": None, "qty": 0} for symbol in TICKERS}

def count_open_positions():
    return sum(1 for symbol in positions if positions[symbol]["open"])

def is_market_open():
    """Check if US market is currently open"""
    eastern = pytz.timezone("US/Eastern")
    now_eastern = datetime.now(eastern)
    
    # Check if weekend
    if now_eastern.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Check market hours (9:30 AM - 4:00 PM ET)
    market_open = now_eastern.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_eastern.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now_eastern <= market_close

def close_all_positions():
    """Close all open positions at end of day"""
    for symbol in TICKERS:
        if positions[symbol]["open"]:
            print(f"End of day: Closing position in {symbol}")
            result = market_sell(symbol)  # This will sell all shares
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

# === Main Bot Loop ===
print("Starting RSI Trading Bot...")

while True:
    try:
        # Current US/Eastern time
        eastern = pytz.timezone("US/Eastern")
        now_eastern = datetime.now(eastern)
        current_time_str = now_eastern.strftime("%H:%M")
        
        # Check if market is open
        if not is_market_open():
            print(f"Market closed at {current_time_str}. Waiting...")
            time.sleep(CHECK_INTERVAL)
            continue
        
        # Sync positions every iteration
        sync_positions()
        
        # Remove end-of-day forced sell logic
        # (No call to close_all_positions at/after 3:55 PM)

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

                    # Always allow selling during market hours
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
                        # Try to get actual fill price from order
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

    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")

    time.sleep(CHECK_INTERVAL)