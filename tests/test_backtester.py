import logging
import unittest
from datetime import datetime

# Silence all logging during unit tests
logging.disable(logging.CRITICAL)

from data_loader import load_market_data
from engine import BacktestEngine
from models import MarketDataPoint, Order, OrderError
from strategies import Strategy


class _AlwaysBuy(Strategy):
    def generate_signals(self, tick: MarketDataPoint):
        return [("BUY", tick.symbol, 1, tick.price)]


class _AlwaysSell(Strategy):
    def generate_signals(self, tick: MarketDataPoint):
        return [("SELL", tick.symbol, 1, tick.price)]


class TestBacktester(unittest.TestCase):
    def test_csv_parsing_into_frozen_dataclass(self):
        ticks = load_market_data("market_data.csv")
        self.assertTrue(len(ticks) > 0)
        self.assertIsInstance(ticks[0], MarketDataPoint)

        # Frozen dataclass: mutation should raise
        with self.assertRaises(Exception):
            ticks[0].price = ticks[0].price + 1.0

    def test_order_is_mutable(self):
        o = Order(action="BUY", symbol="AAPL", quantity=1, price=100.0)
        o.status = "FILLED"
        self.assertEqual(o.status, "FILLED")

    def test_invalid_order_raises(self):
        o = Order(action="BUY", symbol="AAPL", quantity=0, price=100.0)
        with self.assertRaises(OrderError):
            o.validate()

    def test_execution_errors_do_not_stop_backtest(self):
        ticks = [
            MarketDataPoint(datetime(2020, 1, 1, 0, 0, i), "AAPL", 100.0 + i)
            for i in range(30)
        ]
        engine = BacktestEngine([_AlwaysBuy()], initial_cash=10_000.0, fail_rate=1.0, verbose=False)
        result = engine.run(ticks)

        # Should process all ticks even though every execution fails
        self.assertEqual(len(result.equity_curve), len(ticks))
        self.assertTrue(all(o.status == "FAILED" for o in result.orders))

    def test_rejected_orders_do_not_stop_backtest(self):
        ticks = [
            MarketDataPoint(datetime(2020, 1, 1, 0, 0, i), "AAPL", 100.0 + i)
            for i in range(10)
        ]
        engine = BacktestEngine([_AlwaysSell()], initial_cash=10_000.0, fail_rate=0.0, verbose=False)
        result = engine.run(ticks)

        # Should process all ticks and reject sells (no shorting)
        self.assertEqual(len(result.equity_curve), len(ticks))
        self.assertTrue(all(o.status == "REJECTED" for o in result.orders))


if __name__ == "__main__":
    unittest.main()
