import ccxt
import pandas as pd
import time
from datetime import datetime, timedelta
import os
import pybit
from pybit.unified_trading import HTTP

api_key = "xxx"
api_secret = "xxx"
data_path = "data/"

# session = HTTP(
#     test=False,
#     api_key=api_key,
#     api_secret=api_secret
# )

# print(ccxt.exchanges)
# exchange_id = 'bybit'
# exchange = ccxt.bybit({
#     'apiKey': api_key,
#     'secret': api_secret
# })

def _import_price_data(symbol, timeframe, since, limit):
    exchange = ccxt.bybit()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

#pobieranie danych z cache lub z API (krótki termin)
def get_price_data(symbol, timeframe, since, limit):
    filename = f"data/{symbol.replace('/', '_')}_{timeframe}_{since}_{limit}.csv"
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    else:
        df = _import_price_data(symbol, timeframe, since, limit)
        df.to_csv(filename, index=False)
    return df

# pobieranie pełnej historii
def fetch_full_history(symbol="BTC/USDT", timeframe="1h", since="2021-01-01", save_csv=True):
    exchange = ccxt.bybit()
    all_candles = []
    since_ms = int(datetime.fromisoformat(since).timestamp() * 1000)
    
    while True:
        candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since_ms, limit=1000)

        if not candles:
            break  
        
        all_candles.extend(candles)
        
        # przygotowanie do kolejnego zapytania
        since_ms = candles[-1][0] + 1  # ostatni timestamp + 1 ms
        
        print(f"Pobrano {len(all_candles)} świec do {datetime.utcfromtimestamp(candles[-1][0]/1000)}")
        
        time.sleep(1.2)  # unikanie limitów API
    
    df = pd.DataFrame(all_candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    
    if save_csv:
        filename = f"{symbol.replace('/', '_')}_{timeframe}.csv"
        df.to_csv(data_path + filename, index=False)
        print(f"Zapisano do pliku: {filename}")
    
    return df

# ładowanie pliku csv
def load_data_from_csv(symbol, timeframe='1h'):
    filename = f'{symbol.upper()}_USDT_{timeframe}.csv'
    df = pd.read_csv(data_path + filename)
    return df