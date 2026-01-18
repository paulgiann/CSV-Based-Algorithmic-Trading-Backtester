from __future__ import annotations

import math
from typing import Dict, List, Tuple

from models import MarketDataPoint


def periodic_returns(equity_curve: List[Tuple[MarketDataPoint, float]]) -> List[float]:
    rets: List[float] = []
    for i in range(1, len(equity_curve)):
        prev = equity_curve[i - 1][1]
        cur = equity_curve[i][1]
        if prev <= 0:
            continue
        rets.append(cur / prev - 1.0)
    return rets


def total_return(initial_equity: float, final_equity: float) -> float:
    if initial_equity <= 0:
        return 0.0
    return final_equity / initial_equity - 1.0


def sharpe_ratio(returns: List[float]) -> float:
    n = len(returns)
    if n < 2:
        return 0.0
    mean = sum(returns) / n
    var = sum((r - mean) ** 2 for r in returns) / (n - 1)
    std = math.sqrt(var)
    if std == 0:
        return 0.0
    # scaled by sqrt(n) so it is comparable across runs
    return (mean / std) * math.sqrt(n)


def max_drawdown(equity_curve: List[Tuple[MarketDataPoint, float]]) -> float:
    peak = None
    worst = 0.0
    for _, eq in equity_curve:
        if peak is None or eq > peak:
            peak = eq
        if peak and peak > 0:
            dd = eq / peak - 1.0
            if dd < worst:
                worst = dd
    return float(worst)


def _ascii_equity_curve(values: List[float], width: int = 60) -> str:
    if not values:
        return ''

    if len(values) <= width:
        sample = values
    else:
        step = (len(values) - 1) / (width - 1)
        sample = [values[int(round(i * step))] for i in range(width)]

    low = min(sample)
    high = max(sample)
    if high == low:
        return '.' * len(sample)

    chars = ' .:-=+*#%@'
    out = []
    for v in sample:
        t = (v - low) / (high - low)
        idx = int(round(t * (len(chars) - 1)))
        out.append(chars[idx])
    return ''.join(out)


def write_performance_md(
    path: str,
    metrics: Dict[str, float],
    equity_curve: List[Tuple[MarketDataPoint, float]],
    notes: str = ''
) -> None:
    values = [eq for _, eq in equity_curve]
    spark = _ascii_equity_curve(values)

    lines = []
    lines.append('# Backtest Performance')
    lines.append('')
    lines.append('## Summary Metrics')
    lines.append('')
    lines.append('| Metric | Value |')
    lines.append('|---|---:|')
    for k, v in metrics.items():
        if k in ('Total Return', 'Max Drawdown'):
            lines.append(f'| {k} | {v:.2%} |')
        else:
            lines.append(f'| {k} | {v:.4f} |')
    lines.append('')
    lines.append('## Equity Curve (ASCII)')
    lines.append('')
    lines.append('```')
    lines.append(spark)
    lines.append('```')
    lines.append('')
    lines.append('## Interpretation')
    lines.append('')
    if notes:
        lines.append(notes.strip())
    else:
        lines.append(
            'This is a simple tick-level simulation with basic strategies. '
            'Sharpe is computed from tick returns (not annualized), so treat it as a relative score '
            'for comparing runs using the same data and settings.'
        )

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
