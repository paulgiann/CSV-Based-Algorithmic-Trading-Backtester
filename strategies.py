from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple

from models import MarketDataPoint


Signal = Tuple[str, str, int, float]  # (action, symbol, qty, price)


class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> List[Signal]:
        raise NotImplementedError


class MovingAverageCrossoverStrategy(Strategy):
    def __init__(self, symbol: str, short_window: int = 5, long_window: int = 20, order_size: int = 10):
        if short_window <= 0 or long_window <= 0 or short_window >= long_window:
            raise ValueError('windows must be positive and short_window < long_window')

        self._symbol = symbol
        self._short = short_window
        self._long = long_window
        self._order_size = order_size

        self._prices: List[float] = []
        self._last_state = 0  # -1 below, +1 above

    def generate_signals(self, tick: MarketDataPoint) -> List[Signal]:
        if tick.symbol != self._symbol:
            return []

        self._prices.append(tick.price)
        if len(self._prices) < self._long:
            return []

        short_ma = sum(self._prices[-self._short:]) / self._short
        long_ma = sum(self._prices[-self._long:]) / self._long

        state = 1 if short_ma > long_ma else -1 if short_ma < long_ma else 0
        signals: List[Signal] = []

        if self._last_state != 0 and state != 0 and state != self._last_state:
            if state > 0:
                signals.append(('BUY', tick.symbol, self._order_size, tick.price))
            else:
                signals.append(('SELL', tick.symbol, self._order_size, tick.price))

        self._last_state = state if state != 0 else self._last_state
        return signals


class MomentumStrategy(Strategy):
    def __init__(self, symbol: str, lookback: int = 10, threshold: float = 0.01, order_size: int = 10):
        if lookback <= 0:
            raise ValueError('lookback must be positive')
        if threshold < 0:
            raise ValueError('threshold must be non-negative')

        self._symbol = symbol
        self._lookback = lookback
        self._threshold = threshold
        self._order_size = order_size

        self._prices: List[float] = []
        self._last_action = None

    def generate_signals(self, tick: MarketDataPoint) -> List[Signal]:
        if tick.symbol != self._symbol:
            return []

        self._prices.append(tick.price)
        if len(self._prices) <= self._lookback:
            return []

        prev = self._prices[-(self._lookback + 1)]
        if prev <= 0:
            return []

        ret = (tick.price / prev) - 1.0
        signals: List[Signal] = []

        if ret > self._threshold and self._last_action != 'BUY':
            signals.append(('BUY', tick.symbol, self._order_size, tick.price))
            self._last_action = 'BUY'
        elif ret < -self._threshold and self._last_action != 'SELL':
            signals.append(('SELL', tick.symbol, self._order_size, tick.price))
            self._last_action = 'SELL'

        return signals
