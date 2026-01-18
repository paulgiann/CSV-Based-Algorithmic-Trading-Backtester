from __future__ import annotations

from dataclasses import dataclass
import datetime as dt


@dataclass(frozen=True)
class MarketDataPoint:
    timestamp: dt.datetime
    symbol: str
    price: float


class OrderError(Exception):
    """Raised for invalid orders."""


class ExecutionError(Exception):
    """Raised for simulated execution failures."""


class Order:
    """Mutable order used during simulation."""

    def __init__(self, action: str, symbol: str, quantity: int, price: float, status: str = "NEW"):
        self.action = str(action).upper().strip()
        self.symbol = str(symbol).strip()
        self.quantity = int(quantity)
        self.price = float(price)
        self.status = status

    def validate(self) -> None:
        if self.action not in ("BUY", "SELL"):
            raise OrderError(f"Invalid action: {self.action}")
        if not self.symbol:
            raise OrderError("Missing symbol")
        if self.quantity <= 0:
            raise OrderError("Quantity must be positive")
        if self.price <= 0:
            raise OrderError("Price must be positive")

    def __repr__(self) -> str:
        return (
            f"Order(action={self.action}, symbol={self.symbol}, quantity={self.quantity}, "
            f"price={self.price}, status={self.status})"
        )
