from scripts.bb_data_load import get_price_data, fetch_full_history, load_data_from_csv
import pandas as pd
from scripts.tools import TechnicalIndicators
from scripts.tools import GenerateLevels
from scripts.simulation import Simulation

# df = get_price_data('BTC/USDT', '1h', None, 1000)
# df = fetch_full_history(symbol="BTC/USDT", timeframe="1h", since="2021-01-01", save_csv=True)

## Podstawowe załadowanie dancyh
# df = load_data_from_csv('BTC', '1h')
# print(df)
# ti = TechnicalIndicators()
# df = ti.get_indicators(df)


### praca z danymi testowymi. Pominięcie wczytywania i aplikowania indykatorów
# df = pd.read_csv('data/BTC_USDT_1h.csv')
# levels(df)
# ti = TechnicalIndicators()
# df = ti.get_indicators(df)
# df.to_csv('data/BTC_USDT_1h_t_full.csv', index=False)


### ładowanie danych lokalnych
df = pd.read_csv('data/BTC_USDT_1h_t_full.csv')

gl = GenerateLevels(df)
levels_list = gl.levels()
simulation = Simulation(df, levels_list)
simulation.launch_simulation()

