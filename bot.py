from config import BybitConfig
from pybit.unified_trading import HTTP
import urllib3
import logging
from pathlib import Path
from typing import Optional
from functools import lru_cache
from decimal import Decimal
import time


logger = logging.getLogger(__name__)


def setup_logging(log_file: str | Path = "trade_log.txt") -> None:
    """Configure logging to console and append to a text file."""
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, mode="a", encoding="utf-8"),
        ],
        force=True,
    )


class BybitTradingBot:
    """Simple helper for placing and closing Bybit linear USDT orders."""

    ALLOWED_SYMBOLS = [
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
        "XRPUSDT",
        "DOGEUSDT",
        "BNBUSDT",
    ]

    def __init__(self, session: HTTP):
        self.session = session

    def _validate(self, symbol: str, amount: float, leverage: int) -> None:
        if symbol not in self.ALLOWED_SYMBOLS:
            raise ValueError("Unsupported trading pair")
        if not 80 <= amount <= 120:
            raise ValueError("Amount must be between 80 and 120 USD")
        if not 10 <= leverage <= 20:
            raise ValueError("Leverage must be between 10 and 20")
        notional = amount * leverage
        if not 800 <= notional <= 1200:
            raise ValueError("Position value must be between 800 and 1200 USD")

    def _last_price(self, symbol: str) -> float:
        """Return last traded price for symbol."""
        result = self.session.get_tickers(category="linear", symbol=symbol)
        price = (
            result.get("result", {})
            .get("list", [{}])[0]
            .get("lastPrice")
        )
        if price is None:
            raise ValueError(f"No price data for {symbol}")
        return float(price)

    @lru_cache(maxsize=None)
    def _lot_step(self, symbol: str) -> tuple[float, float]:
        """Return quantity step and minimum order size for symbol."""
        result = self.session.get_instruments_info(
            category="linear", symbol=symbol
        )
        info = result.get("result", {}).get("list", [{}])[0].get(
            "lotSizeFilter", {}
        )
        step = float(info.get("qtyStep", 1))
        min_qty = float(info.get("minOrderQty", step))
        return step, min_qty

    def _format_qty(self, symbol: str, qty: float) -> float:
        """Round quantity to exchange step size."""
        step, min_qty = self._lot_step(symbol)
        d_step = Decimal(str(step))
        d_qty = Decimal(str(qty))
        d_min = Decimal(str(min_qty))
        adjusted = (d_qty // d_step) * d_step
        if adjusted < d_min:
            adjusted = d_min
        return float(adjusted)

    def _set_leverage(self, symbol: str, leverage: int) -> None:
        """Safely set leverage ignoring non-modification errors."""
        try:
            self.session.set_leverage(
                category="linear",
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage),
            )
        except Exception as exc:  # pragma: no cover - network errors
            msg = str(exc)
            if "110043" in msg or "leverage not modified" in msg.lower():
                logger.info(f"{symbol}: leverage already set to {leverage}")
            else:
                raise

    def _calculate_sl_tp(self, symbol: str, side: str) -> tuple[float, float]:
        """Determine stop-loss and take-profit using support/resistance and trend."""
        long = self.session.get_kline(
            category="linear", symbol=symbol, interval=15, limit=50
        )
        short = self.session.get_kline(
            category="linear", symbol=symbol, interval=5, limit=50
        )
        long_c = [float(c[4]) for c in long.get("result", {}).get("list", [])]
        short_c = [float(c[4]) for c in short.get("result", {}).get("list", [])]
        if not long_c or not short_c:
            raise ValueError(f"No kline data for {symbol}")
        support = min(long_c)
        resistance = max(long_c)
        trend_up = short_c[-1] >= short_c[0]
        price = self._last_price(symbol)
        if side == "Buy":
            stop = min(support, price * 0.99)
            take = max(resistance, price * (1.02 if trend_up else 1.01))
        else:
            stop = max(resistance, price * 1.01)
            take = min(support, price * (0.98 if trend_up else 0.99))
        return stop, take

    def place_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        leverage: int,
        stop_loss: float,
        take_profit: float,
    ) -> dict:
        """Place a market order respecting risk limits."""
        if stop_loss is None or take_profit is None:
            raise ValueError("Stop loss and take profit required")
        self._validate(symbol, amount, leverage)
        price = self._last_price(symbol)
        if side == "Buy" and not (stop_loss < price < take_profit):
            raise ValueError("Invalid SL/TP levels")
        if side == "Sell" and not (take_profit < price < stop_loss):
            raise ValueError("Invalid SL/TP levels")
        qty = self._format_qty(symbol, amount * leverage / price)
        self._set_leverage(symbol, leverage)
        return self.session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=str(qty),
            timeInForce="ImmediateOrCancel",
            stopLoss=str(stop_loss),
            takeProfit=str(take_profit),
        )

    def close_position(
        self, symbol: str, side: str, amount: float, leverage: int
    ) -> dict:
        """Close an existing position by placing an opposite market order."""
        self._validate(symbol, amount, leverage)
        price = self._last_price(symbol)
        qty = self._format_qty(symbol, amount * leverage / price)
        close_side = "Sell" if side == "Buy" else "Buy"
        return self.session.place_order(
            category="linear",
            symbol=symbol,
            side=close_side,
            orderType="Market",
            qty=str(qty),
            timeInForce="ImmediateOrCancel",
            reduceOnly=True,
        )

    def log_market_trend(self, symbol: str) -> None:
        """Fetch last 50 five-minute candles and log price direction."""
        result = self.session.get_kline(
            category="linear", symbol=symbol, interval=5, limit=50
        )
        candles = result.get("result", {}).get("list", [])
        if not candles:
            logger.warning(f"No kline data for {symbol}")
            return
        closes = [float(c[4]) for c in reversed(candles)]
        if closes[-1] > closes[0]:
            trend = "actively bought, price increases"
        elif closes[-1] < closes[0]:
            trend = "actively sold, price decreases"
        else:
            trend = "stable, price unchanged"
        logger.info(f"{symbol}: {trend}")

    def ma_crossover_signal(self, symbol: str) -> str:
        """Return Buy/Sell/Hold using a 5/20 SMA crossover."""
        result = self.session.get_kline(
            category="linear", symbol=symbol, interval=5, limit=50
        )
        candles = result.get("result", {}).get("list", [])
        if len(candles) < 20:
            logger.warning(f"Not enough kline data for {symbol}")
            return "Hold"
        closes = [float(c[4]) for c in reversed(candles)]
        short_sma = sum(closes[-5:]) / 5
        long_sma = sum(closes[-20:]) / 20
        if short_sma > long_sma:
            return "Buy"
        if short_sma < long_sma:
            return "Sell"
        return "Hold"

    def rsi_signal(self, symbol: str, period: int = 14) -> str:
        """Return Buy/Sell/Hold based on RSI indicator."""
        result = self.session.get_kline(
            category="linear", symbol=symbol, interval=5, limit=period + 1
        )
        candles = result.get("result", {}).get("list", [])
        if len(candles) < period + 1:
            logger.warning(f"Not enough kline data for {symbol}")
            return "Hold"
        closes = [float(c[4]) for c in reversed(candles)]
        gains = [max(closes[i] - closes[i - 1], 0) for i in range(1, len(closes))]
        losses = [max(closes[i - 1] - closes[i], 0) for i in range(1, len(closes))]
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - 100 / (1 + rs)
        if rsi < 30:
            return "Buy"
        if rsi > 70:
            return "Sell"
        return "Hold"

    def combined_signal(self, symbol: str) -> str:
        """Return unified trade signal if MA and RSI agree."""
        ma = self.ma_crossover_signal(symbol)
        rsi = self.rsi_signal(symbol)
        if ma == rsi and ma != "Hold":
            return ma
        return "Hold"

    def trade_with_signals(
        self, symbol: str, amount: float, leverage: int
    ) -> Optional[dict]:
        """Execute trade only when multiple signals align."""
        self._validate(symbol, amount, leverage)
        signal = self.combined_signal(symbol)
        if signal == "Hold":
            logger.info(f"{symbol}: no trade signal")
            return None
        stop_loss, take_profit = self._calculate_sl_tp(symbol, signal)
        return self.place_order(
            symbol, signal, amount, leverage, stop_loss, take_profit
        )

    def trade_with_ma(
        self, symbol: str, amount: float, leverage: int
    ) -> Optional[dict]:  # pragma: no cover - backward compatibility
        return self.trade_with_signals(symbol, amount, leverage)

    def log_all_trends(self) -> None:
        for symbol in self.ALLOWED_SYMBOLS:
            self.log_market_trend(symbol)


def main() -> None:  # pragma: no cover - side effects and infinite loop
    cfg = BybitConfig.from_env()
    session = HTTP(
        testnet=cfg.testnet,
        api_key=cfg.api_key,
        api_secret=cfg.api_secret,
        demo=cfg.demo,
    )
    if cfg.ignore_ssl:
        session.client.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    setup_logging()
    bot = BybitTradingBot(session)
    print("Fetching account balance...")
    try:
        result = session.get_wallet_balance(accountType="UNIFIED")
    except Exception as exc:
        print(f"Failed to fetch balance: {exc}")
    else:
        print(result)
    while True:
        bot.log_all_trends()
        for symbol in bot.ALLOWED_SYMBOLS:
            try:
                result = bot.trade_with_signals(symbol, 100, 10)
                if result:
                    logger.info(f"{symbol}: order placed {result}")
            except Exception as exc:
                logger.error(f"{symbol}: trade failed: {exc}")
        time.sleep(60)


if __name__ == "__main__":  # pragma: no cover - script entry point
    main()
