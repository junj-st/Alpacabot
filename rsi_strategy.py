from marketdata import get_latest_price
from trades import percent_market_buy, market_sell
from percentage import getPortfolio_value
from rsi import get_rsi
from orders import getPositions
import time

# === Strategy Parameters ===
SYMBOL = 'AAPL'
RSI_LENGTH = 14
OVERSOLD = 20
STOP_LOSS_PCT = 4.0
TAKE_PROFIT_PCT = 1.0
TRADE_PERCENTAGE = 0.1  # Trade with 10% of portfolio value
CHECK_INTERVAL = 60  # seconds

# === Position Tracking ===
position_open = False
entry_price = None

# === Main Bot Loop ===
while True:
    try:
        df = get_rsi(SYMBOL, RSI_LENGTH)
        rsi_now = df['rsi'].iloc[-1]
        rsi_prev = df['rsi'].iloc[-2]
        latest_price = get_latest_price(SYMBOL)

        # === Entry: RSI Crosses Above Oversold ===
        if not position_open and rsi_prev < OVERSOLD and rsi_now >= OVERSOLD:
            print(f"RSI crossed above {OVERSOLD}. Buying {SYMBOL}...")
            resp = percent_market_buy(SYMBOL, TRADE_PERCENTAGE)
            print(resp)
            entry_price = latest_price
            position_open = True

        # === Exit: Stop Loss or Take Profit ===
        if position_open and entry_price:
            change_pct = (latest_price - entry_price) / entry_price * 100

            if change_pct >= TAKE_PROFIT_PCT:
                print(f"Take profit triggered at {change_pct:.2f}%. Selling {SYMBOL}...")
                market_sell(SYMBOL)
                position_open = False
                entry_price = None

            elif change_pct <= -STOP_LOSS_PCT:
                print(f"Stop loss triggered at {change_pct:.2f}%. Selling {SYMBOL}...")
                market_sell(SYMBOL)
                position_open = False
                entry_price = None

        print(f"RSI: {rsi_now:.2f}, Price: ${latest_price:.2f}, Position: {position_open}, Entry: {entry_price}")
    except Exception as e:
        print(f"[ERROR] {e}")

    time.sleep(CHECK_INTERVAL)