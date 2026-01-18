from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from models import ExecutionError, MarketDataPoint, Order, OrderError
from strategies import Strategy, Signal


logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    initial_cash: float
    final_cash: float
    positions: Dict[str, Dict[str, float]]
    orders: List[Order]
    equity_curve: List[Tuple[MarketDataPoint, float]]  # (tick, equity)


class BacktestEngine:
    def __init__(
        self,
        strategies: List[Strategy],
        initial_cash: float = 10_000.0,
        fail_rate: float = 0.02,
        verbose: bool = True,
    ):
        self._strategies = list(strategies)
        self._initial_cash = float(initial_cash)
        self._fail_rate = float(fail_rate)
        self.verbose = bool(verbose)

        self._cash = float(initial_cash)
        self._positions: Dict[str, Dict[str, float]] = {}
        self._last_price: Dict[str, float] = {}
        self._orders: List[Order] = []
        self._equity_curve: List[Tuple[MarketDataPoint, float]] = []

    def run(self, ticks: List[MarketDataPoint]) -> BacktestResult:
        for tick in ticks:
            self._last_price[tick.symbol] = tick.price

            signals: List[Signal] = []
            for strat in self._strategies:
                try:
                    signals.extend(strat.generate_signals(tick))
                except Exception as e:
                    logger.exception("Strategy error (%s): %s", strat.__class__.__name__, e)

            for sig in signals:
                action, symbol, qty, price = sig
                order = None
                try:
                    order = Order(action=action, symbol=symbol, quantity=qty, price=price)
                    order.validate()
                    self._execute_order(order)
                    order.status = "FILLED"

                except OrderError as e:
                    if order is None:
                        order = Order(action=action, symbol=symbol, quantity=qty, price=price)
                    order.status = "REJECTED"
                    if self.verbose:
                        logger.warning("Order rejected: %s (%s)", order, e)

                except ExecutionError as e:
                    if order is None:
                        order = Order(action=action, symbol=symbol, quantity=qty, price=price)
                    order.status = "FAILED"
                    if self.verbose:
                        logger.warning("Execution failed: %s (%s)", order, e)

                except Exception as e:
                    if order is None:
                        order = Order(action=action, symbol=symbol, quantity=qty, price=price)
                    order.status = "FAILED"
                    logger.exception("Unexpected error on order: %s (%s)", order, e)

                finally:
                    if order is not None:
                        self._orders.append(order)

            equity = self._compute_equity()
            self._equity_curve.append((tick, equity))

        return BacktestResult(
            initial_cash=self._initial_cash,
            final_cash=self._cash,
            positions=self._positions,
            orders=self._orders,
            equity_curve=self._equity_curve,
        )

    def _execute_order(self, order: Order) -> None:
        # Simulate occasional execution failure
        if self._fail_rate > 0 and random.random() < self._fail_rate:
            raise ExecutionError("simulated venue failure")

        symbol = order.symbol
        qty = int(order.quantity)
        price = float(order.price)

        pos = self._positions.get(symbol)
        if pos is None:
            pos = {"quantity": 0.0, "avg_price": 0.0}
            self._positions[symbol] = pos

        held = int(pos["quantity"])

        if order.action == "BUY":
            cost = qty * price
            if cost > self._cash:
                raise OrderError("insufficient cash")

            new_qty = held + qty
            if new_qty <= 0:
                raise OrderError("invalid resulting position")

            # Weighted average price
            if held == 0:
                new_avg = price
            else:
                new_avg = (held * pos["avg_price"] + qty * price) / new_qty

            pos["quantity"] = float(new_qty)
            pos["avg_price"] = float(new_avg)
            self._cash -= cost

        elif order.action == "SELL":
            if qty > held:
                raise OrderError("cannot sell more than held (no shorting)")

            proceeds = qty * price
            new_qty = held - qty
            pos["quantity"] = float(new_qty)
            if new_qty == 0:
                pos["avg_price"] = 0.0
            self._cash += proceeds

        else:
            raise OrderError(f"unknown action: {order.action}")

    def _compute_equity(self) -> float:
        equity = self._cash
        for symbol, pos in self._positions.items():
            qty = int(pos.get("quantity", 0.0))
            if qty == 0:
                continue
            last = self._last_price.get(symbol)
            if last is None:
                continue
            equity += qty * last
        return float(equity)
