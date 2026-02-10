import pytest

from scripts.simulation import Simulation


class FakeSeries:
    def __init__(self, data):
        self.data = list(data)

    @property
    def iloc(self):
        return self

    @property
    def values(self):
        return self.data

    def min(self):
        return min(self.data)

    def max(self):
        return max(self.data)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return FakeSeries(self.data[item])
        return self.data[item]


class FakeILoc:
    def __init__(self, rows):
        self.rows = rows

    def __getitem__(self, item):
        if isinstance(item, slice):
            return FakeFrame(self.rows[item])
        return self.rows[item]


class FakeFrame:
    def __init__(self, rows):
        self.rows = rows
        self.iloc = FakeILoc(rows)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, column):
        return FakeSeries([row[column] for row in self.rows])


@pytest.fixture
def base_df():
    rows = [
        {"timestamp": "t0", "close": 100, "low": 99, "high": 101, "EMA_long": 90, "RSI": 20, "MACD_diff": -2.0},
        {"timestamp": "t1", "close": 101, "low": 100, "high": 102, "EMA_long": 90, "RSI": 25, "MACD_diff": -1.0},
        {"timestamp": "t2", "close": 102, "low": 101, "high": 103, "EMA_long": 90, "RSI": 35, "MACD_diff": -0.5},
        {"timestamp": "t3", "close": 103, "low": 102, "high": 104, "EMA_long": 90, "RSI": 50, "MACD_diff": 0.2},
        {"timestamp": "t4", "close": 104, "low": 103, "high": 105, "EMA_long": 90, "RSI": 60, "MACD_diff": 0.5},
        {"timestamp": "t5", "close": 105, "low": 104, "high": 106, "EMA_long": 90, "RSI": 75, "MACD_diff": 0.8},
    ]
    return FakeFrame(rows)


def test_rsi_long_signal_detects_oversold(base_df):
    sim = Simulation(base_df, levels_list=[])
    sim.rsi_observe_period = 4
    sim.rsi_buy = 30
    assert sim._rsi_long_signal(4) is True


def test_macd_long_signal_detects_recovery_cross(base_df):
    sim = Simulation(base_df, levels_list=[])
    sim.macd_observe_period = 4
    assert sim._macd_long_signal(4) is True


def test_level_signal_respects_buffer(base_df):
    sim = Simulation(base_df, levels_list=[])
    sim.levels_buffer_perc = 0.005
    assert sim._level_signal(100, 101, [100.7]) is True
    assert sim._level_signal(100, 101, [110.0]) is False


def test_launch_simulation_records_trade_result(base_df, monkeypatch):
    sim = Simulation(base_df, levels_list=[101])
    sim.take_profit_perc = 0
    sim.stop_loss_perc = 100

    monkeypatch.setattr(sim, "_rsi_long_signal", lambda i: True)
    monkeypatch.setattr(sim, "_macd_long_signal", lambda i: True)
    monkeypatch.setattr(sim, "_level_signal", lambda p1, p2, lvls: True)

    sim.launch_simulation()

    assert len(sim.results) >= 1
    assert sim.results[0] == pytest.approx(1.0)
