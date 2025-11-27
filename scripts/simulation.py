import numpy as np

class Simulation:
    def __init__(self, df, levels_list):
        self.rsi_buy = 30
        self.rsi_sell = 70
        self.rsi_observe_period = 4
        self.macd_observe_period = 4
        self.macd_cross_value = 0
        self.df = df
        self.take_profit_perc = 5
        self.stop_loss_perc = 1
        self.levels_list = levels_list
        self.levels_buffer_perc = 0.005  # 0.5%

        self.results = []

    # RSI SIGNALS
    # jeśli w okresie obserwowanym RSI spadło poniżej wskazanego poziomu to utwórz sygnał
    def _rsi_long_signal(self, i):
        if self.df.iloc[i-self.rsi_observe_period:i]['RSI'].min() < self.rsi_buy:
            return True
        else:
            return False
        
    def _rsi_short_signal(self, i):
        if self.df.iloc[i-self.rsi_observe_period:i]['RSI'].max() > self.rsi_sell:
            return True
        else:
            return False
        
    # MACD Signals
    # jeśli w okresie obserwowanym MACD 
    def _macd_long_signal(self, i):
        if i < self.macd_observe_period:
            return False   
        
        period_values = self.df.iloc[i-self.macd_observe_period:i]['MACD_diff']
        past_values = period_values[:-1].values
        current_value = period_values.iloc[-1]
        if len(period_values) < self.macd_observe_period:
            return False

        # sprawdzanie warunków sygnału
        prev_negative = (past_values < 0).all() # czy wszystkie poprzednie wartości były ujemne
        prev_are_increasing = np.all(np.diff(past_values) > 0) # czy poprzednie wartości rosną
        current_signal = current_value > self.macd_cross_value # czy aktualna wartość jest powyżej progu
        if prev_negative and prev_are_increasing and current_signal:
            return True
        else:
            return False
        
    def _macd_short_signal(self, i):
        # sprawdzanie czy jest wystarczająco danych
        if i < self.macd_observe_period:
            return False   
        # obserwowany okres oraz obecne wartości

        period_values = self.df.iloc[i-self.macd_observe_period:i]['MACD_diff']
        past_values = period_values[:-1].values
        current_value = period_values.iloc[-1]

        # sprawdzanie warunków sygnału
        prev_positive = (past_values > 0).all() # czy wszystkie poprzednie wartości były dodatnie
        prev_are_decreasing = np.all(np.diff(past_values) < 0) # czy poprzednie wartości maleją
        current_signal = current_value < self.macd_cross_value # czy aktualna wartość jest poniżej progu
        if prev_positive and prev_are_decreasing and current_signal:
            return True
        else:
            return False
        
    def _level_signal(self, price1, price2, levels):
        # jeśli cena będzie między price 1 a price 2 oraz w zasięgu bufora tych cen to zwróć True
        lower_price = min(price1, price2) * (1-self.levels_buffer_perc)
        upper_price = max(price1, price2) * (1+self.levels_buffer_perc)
        signal = any(lower_price < level < upper_price for level in levels)
        return signal

    
    def launch_simulation(self):
        position = 0
        length = 0
        open_price = 0
        for i in range(len(self.df)):
            record = self.df.iloc[i]
            if position == 0:
                if record['close'] > record['EMA_long']:
                    rsi_signal = self._rsi_long_signal(i)
                    macd_signal = self._macd_long_signal(i)
                    levels_signal = self._level_signal(record['close'], record['low'], self.levels_list)
                    # jeśli 2 z 3 warunków spełnione otwórz long
                    if sum([rsi_signal, macd_signal, levels_signal]) >= 2:
                        print(f"Otwarcie LONG @ {record['timestamp']} cena: {record['close']}")
                        print(f"  RSI: {rsi_signal}, MACD: {macd_signal}, Levels: {levels_signal}")
                        position = 1
                        open_price = record['close']
                        length = 0
                        continue
                    

                elif record['close'] < record['EMA_long']:
                    rsi_signal = self._rsi_short_signal(i)
                    macd_signal = self._macd_short_signal(i)
                    levels_signal = self._level_signal(record['close'], record['high'], self.levels_list)
                    # jeśli 2 z 3 warunków spełnione otwórz short
                    if sum([rsi_signal, macd_signal, levels_signal]) >= 2:
                        print(f"Otwarcie SHORT @ {record['timestamp']} cena: {record['close']}")
                        print(f"  RSI: {rsi_signal}, MACD: {macd_signal}, Levels: {levels_signal}")
                        position = -1
                        open_price = record['close']
                        length = 0
                        continue


            if position == 1:
                length += 1
                length_signal = length > 100
                profit_signal = (record['close'] - open_price)/open_price*100 >= self.take_profit_perc
                level_signal = self._level_signal(open_price, record['high'], self.levels_list)
                ### wyjście z pozycji tp
                # 1. jeśli pozycja jest otwarta dostatecznie długo (pow 100h)
                # 2. jeśli zysk osiągnął 5%
                # 3. jeśli dotarto do poziomu oporu/wsparcia
                # gdy 2 z 3 warunków są spełnione zamknij pozycję 
                ### wyjście z pozycji sl
                # jeśli strata osiągnęła 1%
                if sum([length_signal, profit_signal, level_signal]) >= 2:
                    print(f"Zamknięcie LONG @ {record['timestamp']}")
                    print(f"Take Profit: {(record['close'] - open_price)/open_price*100:.2f}% TIME:{length_signal} PROFIT:{profit_signal} LEVEL:{level_signal}")
                    position = 0
                    length = 0
                    self.results.append((record['close'] - open_price)/open_price*100)
                if (open_price - record['close'])/open_price*100 >= self.stop_loss_perc:
                    print(f"Zamknięcie LONG @ {record['timestamp']}")
                    print(f"Stop Loss: {(record['close'] - open_price)/open_price*100:.2f}%")
                    position = 0
                    length = 0
                    self.results.append((record['close'] - open_price)/open_price*100)
            if position == -1:
                length += 1
                length_signal = length > 100
                profit_signal = (open_price - record['close'])/open_price*100 >= self.take_profit_perc
                level_signal = self._level_signal(open_price, record['low'], self.levels_list)
                if sum([length_signal, profit_signal, level_signal]) >= 2:
                    print(f"Zamknięcie SHORT @ {record['timestamp']}")
                    print(f"Take Profit: {(open_price - record['close'])/open_price*100:.2f}%  TIME:{length_signal} PROFIT:{profit_signal} LEVEL:{level_signal}")
                    position = 0
                    length = 0
                    self.results.append((open_price - record['close'])/open_price*100)
                if (record['close'] - open_price)/open_price*100 >= self.stop_loss_perc:
                    print(f"Zamknięcie SHORT @ {record['timestamp']}")
                    print(f"Stop Loss: {(open_price - record['close'])/open_price*100:.2f}%")
                    position = 0
                    length = 0
                    self.results.append((open_price - record['close'])/open_price*100)
        print("=== SIMULATION RESULTS ===")
        print(f"Liczba transakcji: {len(self.results)}")
        print(f"Średni zysk/strata na transakcję: {np.mean(self.results):.2f}%")
        print(f"Maksymalny zysk: {np.max(self.results):.2f}%")
        print(f"Maksymalna strata: {np.min(self.results):.2f}%")
        winning_trades = [res for res in self.results if res > 0]
        losing_trades = [res for res in self.results if res <= 0]
        print(f"Liczba zyskownych transakcji: {len(winning_trades)}")
        print(f"Liczba stratnych transakcji: {len(losing_trades)}")
        if len(winning_trades) > 0:
            print(f"Średni zysk na zyskownej transakcji: {np.mean(winning_trades):.2f}%")
        if len(losing_trades) > 0:
            print(f"Średnia strata na stratnej transakcji: {np.mean(losing_trades):.2f}%")  
        print(f"Procent zyskownych transakcji: {len(winning_trades)/len(self.results)*100:.2f}%")
