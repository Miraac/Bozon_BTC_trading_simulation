### Wskaźnik do użycia
# 1
# MA 10 / 30
# RSI
# MACD
# Bollinger Bands

### modele uczenia maszynowego
# Random Forest, XGBoost, Neural Networks - klasyfikacja
# Deep Learning - LSTM - analiza szeregów czasowych do prognozowania cen
# Regresja - przewidywanie zmian %

import pandas as pd
import ta

# biblioteki do poziomów technicznych
import yahooquery as yq
import scipy as sp
import mplfinance as mpf
from scipy import signal
import numpy as np

from sklearn.cluster import DBSCAN

class TechnicalIndicators:
    def __init__(self):
        self.ema_short = 10
        self.ema_long = 30
        self.rsi_period = 14
        self.macd_short = 12
        self.macd_long = 26
        self.macd_signal = 9
        self.bb_window = 20
        self.bb_window_dev = 2

    def _ema(self, df):
        df['EMA_short'] = ta.trend.ema_indicator(df['close'], window=self.ema_short)
        df['EMA_long'] = ta.trend.ema_indicator(df['close'], window=self.ema_long)
        return df

    def _rsi(self, df):
        df['RSI'] = ta.momentum.rsi(df['close'], window=self.rsi_period)
        return df

    def _macd(self, df):
        macd_indicator = ta.trend.MACD(df['close'], window_slow=self.macd_long, window_fast=self.macd_short, window_sign=self.macd_signal)
        df['MACD'] = macd_indicator.macd()
        df['MACD_signal'] = macd_indicator.macd_signal()
        df['MACD_diff'] = macd_indicator.macd_diff()
        return df

    def _bollinger_bands(self, df):
        bb_indicator = ta.volatility.BollingerBands(df['close'], window=self.bb_window, window_dev=self.bb_window_dev)
        df['BB_high'] = bb_indicator.bollinger_hband()
        df['BB_low'] = bb_indicator.bollinger_lband()
        df['BB_mavg'] = bb_indicator.bollinger_mavg()
        df['BB_pct'] = bb_indicator.bollinger_pband()
        return df
    
    def _get_price_change(self, df):
        df['change'] = df['close'].pct_change() * 100
        return df

    def get_indicators(self, df):
        df = self._ema(df)
        df = self._rsi(df)
        df = self._macd(df)
        df = self._bollinger_bands(df)
        df = self._get_price_change(df)
        df.dropna(inplace=True)
        return df
    


    
    def save_to_csv(self, df, filename):
        df.to_csv(filename, index=False)

class GenerateLevels:
    def __init__(self, df):
        self.df = df
        # <<<objaśnienie zmiennych>>>
        # peak_dist - minimalna odległość między silnymi szczytami (w liczbie świec czyli godzin)
        # siła szczytu - prominence - im większa tym bardziej wyróżniający się szczyt
        # silne poziomy oporu
        self.strong_peak_dist = 200
        self.strong_perc_prox_width = 0.018  # procentowa odległość cenowa między poziomami do zagęszczenia
        # słabsze poziomy oporu
        self.peak_dist = 100
        self.perc_prox_width = 0.008  # procentowa odległość cenowa między poziomami do zagęszczenia ## dynamiczne skalowanie
        # clustering
        self.eps = 1500  # maksymalna odległość między punktami w klastrze eg ceny
        self.min_samples = 2  # minimalna liczba poziomów w klastrze


    # technical levels
    def _peak_levels(self, side='high', distance=None, perc_scale_prox_width=None):
        # jeśli nie podano wartości
        distance = distance or self.strong_peak_dist

        
        # 1. wykrycie wszystkich kandydatów na szczyty
        candidate_peaks, _ = sp.signal.find_peaks(
            self.df[side],
            distance=distance,
            prominence=0
        )
        # 2. filtrowanie adaptacyjne
        final_peaks = []
        for p in candidate_peaks:
            strong_prom, _ = self._autoscale_params_for_index(p, side)

            left = max(0, p-5)
            right = min(len(self.df), p+5)
            local_min = self.df.iloc[left:right][side].min()
            prom = self.df.iloc[p][side] - local_min

            if prom >= strong_prom:
                final_peaks.append(p)


        # tworzenie listy wartości silnych szczytów
        peaks_values = self.df.iloc[final_peaks][side].values.tolist()
        # dodanie rocznych maksimów (do poprawy)
        # yearly_high = self.df[side].iloc[-252:].max()
        # peaks_values.append(yearly_high) # wcześniejszy return
        # print('done1')

        peak_rank = {p: 0 for p in final_peaks}
        for i, current_peak in enumerate(final_peaks):
            print(f'Processing peak {i+1}/{len(final_peaks)}', end='\r')
            curr_price = self.df.iloc[current_peak][side]
            _, prox_width = self._autoscale_params_for_index(current_peak, side, perc_scale_prox_width)

            for previous_peak in final_peaks[:i]:
                prev_price = self.df.iloc[previous_peak][side]

                if abs(curr_price - prev_price) <= prox_width:
                    peak_rank[current_peak] += 1 
        return peaks_values, peak_rank
        ### wykres z silnymi poziomami
        # add_plot = [mpf.make_addplot(np.full(df.shape[0], resistance), color='r', linestyle='--') for resistance in strong_peaks_values]
        # mpf.plot(
        #     df, 
        #     type='candle', 
        #     style='charles', 
        #     title='price',
        #     volume=True, 
        #     addplot=add_plot
        # )
    
    def _autoscale_params_for_index(self, idx, side='high', prox_width_scale=None):
        """
        Dynamiczne skalowanie parametrów na podstawie ostatnich X świec.
        """
        window = 500  # np. ostatnie 500 godzin (~3 tygodnie)
        start = max(0, idx - window)
        end = idx + 1

        local_slice = self.df.iloc[start:end]
        median_price = local_slice[side].median()

        # Skalowanie
        strong_prom = median_price * 0.015
        prox_width = median_price * (prox_width_scale if prox_width_scale is not None else 0.01)
        return strong_prom, prox_width

    
    def _cluster_levels(self, values):
        #przekształcenie do tablicy
        X = np.array(values).reshape(-1, 1)
        db = DBSCAN(eps=self.eps, min_samples=self.min_samples).fit(X)
        levels = []

        for cluster_label in set(db.labels_):
            if cluster_label == -1:
                continue  # pomijanie szumów
            cluster_points = X[db.labels_ == cluster_label]
            level = np.mean(cluster_points)
            levels.append(level)
        levels.sort()
        return levels   
    
    def _plot(self, levels_dict):
        add_plots = []
        colors = {"strong high": "red",
                  "weak high": "orange",
                  "strong low": "green",
                  "weak low": "cyan"}
        
        for name, levels in levels_dict.items():
            color = colors.get(name, "gray")
            for lvl in levels:
                arr = np.full(len(self.df), lvl)
                add_plots.append(
                    mpf.make_addplot(arr, color=color, linestyle="--")
                )

        mpf.plot(
            self.df.set_index(pd.to_datetime(self.df['timestamp'])),
            type="candle",
            style="charles",
            volume=False,
            addplot=add_plots,
            
        )

    def levels(self):
        print("Generating levels...")
        # poziomy dla szczytów świec "high"
        strong_peaks_values_high, strong_peak_rank_high = self._peak_levels(side='high', 
                                                                            distance=self.strong_peak_dist, 
                                                                            perc_scale_prox_width=self.strong_perc_prox_width
                                                                            )
        weak_peaks_values_high, weak_peak_rank_high = self._peak_levels(side='high', 
                                                                        distance=self.peak_dist, 
                                                                        perc_scale_prox_width=self.perc_prox_width
                                                                        )
        # poziomy dla dołków świec "low"
        strong_peaks_values_low, strong_peak_rank_low = self._peak_levels(side='low', 
                                                                          distance=self.strong_peak_dist, 
                                                                          perc_scale_prox_width=self.strong_perc_prox_width
                                                                          )
        weak_peaks_values_low, weak_peak_rank_low = self._peak_levels(side='low', 
                                                                      distance=self.peak_dist, 
                                                                      perc_scale_prox_width=self.perc_prox_width
                                                                      )
        print("Clustering levels...")

        # 2 sposoby na wyznaczenie poziomów:
        # skomplikowany - uwzględnienie siły poziomów - preak_rank + peak_values
        # prosty - sama klasteryzacja poziomów - peak_values
        # na obecny moment wybieram prosty
        strong_cluster_levels_high = self._cluster_levels(strong_peaks_values_high)
        weak_cluster_levels_high = self._cluster_levels(weak_peaks_values_high)
        strong_cluster_levels_low = self._cluster_levels(strong_peaks_values_low)
        weak_cluster_levels_low = self._cluster_levels(weak_peaks_values_low)
        print(type(strong_cluster_levels_high))
        print(len(strong_cluster_levels_high), 
              len(weak_cluster_levels_high), 
              len(strong_cluster_levels_low), 
              len(weak_cluster_levels_low))
        all_levels = strong_cluster_levels_high + weak_cluster_levels_high + strong_cluster_levels_low + weak_cluster_levels_low
        print(f'Total levels generated: {len(all_levels)}')
        
        # self._plot(
        #       {
        #           "strong high": strong_cluster_levels_high,
        #           "weak high": weak_cluster_levels_high,
        #           "strong low": strong_cluster_levels_low,
        #           "weak low": weak_cluster_levels_low
        #       }
        # )
        return all_levels




    




### mechanizm do klasyfikacji i predykcji
# class PredictionModels:
#     def __init__(self):
#         self.weights = [0.27, 0.23, 0.18, 0.14, 0.10, 0.08]
#         self.h = len(self.weights)
#         self.threshold1 = 0.5
#         self.threshold2 = 0.3

#     def zmienna_objasniajaca(self, df):
#         for n, val in enumerate(self.weights):


