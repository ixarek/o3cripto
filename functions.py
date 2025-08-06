from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

__all__ = [
    "calculate_dynamic_order_size",
    "apply_trailing_stop",
    "partial_take_profit",
    "limit_open_positions",
    "select_strategy",
    "dynamic_leverage",
    "reload_config",
    "cache_candles",
    "log_performance_metrics",
    "sma_crossover",
    "breakout",
    "mean_reversion",
]


def calculate_dynamic_order_size(balance: float, volatility: float, risk_pct: float = 1.0) -> float:
    """Return position size as percentage of balance adjusted by volatility.

    The higher the volatility, the smaller the resulting size. ``risk_pct`` is the
    percentage of the balance to use when volatility is zero.
    """

    if balance < 0:
        raise ValueError("balance must be non-negative")
    if volatility < 0:
        raise ValueError("volatility must be non-negative")
    if risk_pct <= 0:
        raise ValueError("risk_pct must be positive")
    return balance * (risk_pct / 100.0) / (1 + volatility)


def apply_trailing_stop(
    side: str,
    entry_price: float,
    current_price: float,
    trail_pct: float,
    current_sl: Optional[float] = None,
) -> float:
    """Return new stop-loss level applying a trailing percentage.

    ``side`` must be ``"Buy"`` for long positions or ``"Sell"`` for shorts.
    ``current_sl`` is the existing stop-loss (if any).
    """

    if trail_pct <= 0:
        raise ValueError("trail_pct must be positive")
    if side not in {"Buy", "Sell"}:
        raise ValueError("side must be 'Buy' or 'Sell'")

    if side == "Buy":
        base_sl = entry_price * (1 - trail_pct / 100)
        new_sl = current_price * (1 - trail_pct / 100)
        return max(current_sl or base_sl, new_sl)
    else:
        base_sl = entry_price * (1 + trail_pct / 100)
        new_sl = current_price * (1 + trail_pct / 100)
        return min(current_sl or base_sl, new_sl)


def partial_take_profit(
    position_qty: float, targets: Sequence[Tuple[float, float]]
) -> List[Dict[str, float]]:
    """Return list of orders closing parts of the position.

    ``targets`` is a sequence of ``(price, percent)`` pairs where ``percent`` is the
    percentage of the original position size to close at that price.
    """

    orders = []
    for price, percent in targets:
        if percent <= 0:
            raise ValueError("percent must be positive")
        qty = position_qty * percent / 100.0
        orders.append({"price": price, "qty": qty})
    return orders


def limit_open_positions(open_positions: Sequence[str], limit: int) -> bool:
    """Return ``True`` if a new position can be opened without exceeding ``limit``."""

    return len(open_positions) < limit


# Dummy strategy functions used by ``select_strategy``

def sma_crossover(*args, **kwargs):
    pass


def breakout(*args, **kwargs):
    pass


def mean_reversion(*args, **kwargs):
    pass


def select_strategy(
    config: Dict[str, str],
    strategies: Optional[Dict[str, Callable]] = None,
) -> Callable:
    """Select a trading strategy function based on configuration."""

    strategies = strategies or {
        "sma_crossover": sma_crossover,
        "breakout": breakout,
        "mean_reversion": mean_reversion,
    }
    name = config.get("strategy")
    if name not in strategies:
        raise ValueError("Unknown strategy")
    return strategies[name]


def dynamic_leverage(
    base_leverage: int,
    volatility: float,
    max_leverage: int = 20,
    min_leverage: int = 1,
) -> int:
    """Adjust leverage based on volatility."""

    if volatility < 0:
        raise ValueError("volatility must be non-negative")
    lev = int(base_leverage / (1 + volatility))
    return max(min_leverage, min(max_leverage, lev))


def reload_config(config_path: str | Path, current_config: Dict) -> Dict:
    """Reload configuration from JSON file and update ``current_config``."""

    path = Path(config_path)
    with path.open("r", encoding="utf-8") as f:
        new_conf = json.load(f)
    current_config.update(new_conf)
    return current_config


def cache_candles(
    symbol: str, candles: Iterable, cache_dir: str | Path = "cache"
) -> Path:
    """Save candles for ``symbol`` to ``cache_dir`` as JSON and return the path."""

    path = Path(cache_dir)
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / f"{symbol}.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(list(candles), f)
    return file_path


def log_performance_metrics(
    api_latency: float,
    strategy_time: float,
    log_file: str | Path = "performance.log",
) -> None:
    """Append API and strategy timing metrics to ``log_file``."""

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("performance")
    handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.info(
        "api_latency=%.3fs strategy_time=%.3fs", api_latency, strategy_time
    )
    handler.close()
    logger.handlers.clear()
