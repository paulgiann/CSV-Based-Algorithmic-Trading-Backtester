import argparse
import logging

from data_loader import load_market_data
from engine import BacktestEngine
from reporting import max_drawdown, periodic_returns, sharpe_ratio, total_return, write_performance_md
from strategies import MomentumStrategy, MovingAverageCrossoverStrategy


def run_backtest(csv_path: str, report_path: str, fail_rate: float = 0.02) -> None:
    ticks = load_market_data(csv_path)
    if not ticks:
        raise SystemExit('No market data loaded.')

    symbol = ticks[0].symbol

    strategies = [
        MovingAverageCrossoverStrategy(symbol=symbol, short_window=5, long_window=20, order_size=10),
        MomentumStrategy(symbol=symbol, lookback=10, threshold=0.01, order_size=10),
    ]

    engine = BacktestEngine(strategies=strategies, initial_cash=10_000.0, fail_rate=fail_rate)
    result = engine.run(ticks)

    equity_curve = result.equity_curve
    initial_eq = equity_curve[0][1]
    final_eq = equity_curve[-1][1]

    rets = periodic_returns(equity_curve)
    metrics = {
        'Total Return': total_return(initial_eq, final_eq),
        'Sharpe Ratio': sharpe_ratio(rets),
        'Max Drawdown': max_drawdown(equity_curve),
    }

    tr = metrics['Total Return']
    direction = 'gain' if tr >= 0 else 'loss'
    notes = (
        f'Final equity was {final_eq:.2f} starting from {initial_eq:.2f}. '
        f'Total return was {tr:.2%} ({direction}). '
        'Max drawdown captures the worst peak-to-trough loss.'
    )

    write_performance_md(report_path, metrics, equity_curve, notes=notes)

    filled = sum(1 for o in result.orders if o.status == 'FILLED')
    failed = sum(1 for o in result.orders if o.status == 'FAILED')
    rejected = sum(1 for o in result.orders if o.status == 'REJECTED')

    print(f'Data points: {len(ticks)}')
    print(f'Orders: {len(result.orders)} (filled={filled}, rejected={rejected}, failed={failed})')
    print(f'Final cash: {result.final_cash:.2f}')
    print(f'Positions: {result.positions}')
    print(f'Report written: {report_path}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', default='market_data.csv', help='Path to market_data.csv')
    parser.add_argument('--report', default='performance.md', help='Output markdown report path')
    parser.add_argument('--fail-rate', type=float, default=0.02, help='Simulated execution failure probability')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    run_backtest(args.csv, args.report, fail_rate=args.fail_rate)


if __name__ == '__main__':
    main()
