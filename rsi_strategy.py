from marketdata import get_latest_price
from trades import percent_market_buy, market_sell
from rsi import get_rsi
import time
from datetime import datetime
import pytz

# === Strategy Parameters ===
TICKERS = [
    'SOXL', 'HIMS', 'ORCL', 'USB', 'ABNB', 'MMM', 'MU', 'BA',
    'COF', 'MAR', 'PNC', 'VZ', 'DELL', 'NVDL', 'AMD', 'MSFL'
]
RSI_LENGTH = 14
OVERSOLD = 20
STOP_LOSS_PCT = 3.0
TAKE_PROFIT_PCT = 1.0
TRADE_PERCENTAGE = 0.20  # 20% per position
CHECK_INTERVAL = 60  # seconds
SELL_CUTOFF_TIME = "15:55"  # 3:55 PM Eastern Time

# === Position Tracking per Ticker ===
positions = {symbol: {"open": False, "entry_price": None} for symbol in TICKERS}

# === Main Bot Loop ===
while True:
    try:
        # Current US/Eastern time
        eastern = pytz.timezone("US/Eastern")
        now_eastern = datetime.now(eastern)
        current_time_str = now_eastern.strftime("%H:%M")

        for symbol in TICKERS:
            try:
                df = get_rsi(symbol, RSI_LENGTH)
                if df is None or df['rsi'].isna().iloc[-1]:
                    continue

                rsi_now = df['rsi'].iloc[-1]
                rsi_prev = df['rsi'].iloc[-2]
                latest_price = get_latest_price(symbol)

                # === End-of-day Exit ===
                if current_time_str >= SELL_CUTOFF_TIME and positions[symbol]["open"]:
                    print(f"[EOD] {symbol}: Selling before close.")
                    market_sell(symbol)
                    positions[symbol] = {"open": False, "entry_price": None}
                    continue

                # === Entry Signal ===
                if not positions[symbol]["open"] and rsi_prev < OVERSOLD and rsi_now >= OVERSOLD:
                    print(f"{symbol}: RSI crossed above {OVERSOLD}. Buying...")
                    resp = percent_market_buy(symbol, TRADE_PERCENTAGE)
                    print(resp)
                    positions[symbol]["open"] = True
                    positions[symbol]["entry_price"] = latest_price
                    continue

                # === Exit Signal (TP/SL) ===
                if positions[symbol]["open"]:
                    entry = positions[symbol]["entry_price"]
                    change_pct = (latest_price - entry) / entry * 100

                    if change_pct >= TAKE_PROFIT_PCT:
                        print(f"{symbol}: Take Profit hit (+{change_pct:.2f}%). Selling...")
                        market_sell(symbol)
                        positions[symbol] = {"open": False, "entry_price": None}

                    elif change_pct <= -STOP_LOSS_PCT:
                        print(f"{symbol}: Stop Loss hit ({change_pct:.2f}%). Selling...")
                        market_sell(symbol)
                        positions[symbol] = {"open": False, "entry_price": None}

                print(f"{symbol}: RSI={rsi_now:.2f}, Price=${latest_price:.2f}, Entry={positions[symbol]['entry_price']}, Position={positions[symbol]['open']}, Time={current_time_str}")

            except Exception as stock_error:
                print(f"[ERROR] Failed for {symbol}: {stock_error}")

    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")

    time.sleep(CHECK_INTERVAL)
