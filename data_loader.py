import csv
import datetime as dt
import logging
from typing import List

from models import MarketDataPoint


logger = logging.getLogger(__name__)


def load_market_data(csv_path: str) -> List[MarketDataPoint]:
    data: List[MarketDataPoint] = []

    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            try:
                ts_raw = (row.get('timestamp') or '').strip()
                symbol = (row.get('symbol') or '').strip()
                price_raw = (row.get('price') or '').strip()

                if not ts_raw or not symbol or not price_raw:
                    raise ValueError('missing required fields')

                timestamp = dt.datetime.fromisoformat(ts_raw)
                price = float(price_raw)

                data.append(MarketDataPoint(timestamp=timestamp, symbol=symbol, price=price))
            except Exception as e:
                logger.warning('Skipping bad row %d: %s (%s)', i, row, e)

    data.sort(key=lambda x: x.timestamp)
    return data
