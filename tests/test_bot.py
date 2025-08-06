import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Добавляем путь к родительской папке, чтобы импортировать bot.py
sys.path.append(str(Path(__file__).resolve().parents[1]))

from bot import BybitTradingBot  # импорт класса из твоего основного бота


class TestBybitTradingBot(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.session.get_tickers.return_value = {
            "result": {"list": [{"lastPrice": "100"}]}
        }
        self.bot = BybitTradingBot(self.session)

    def test_place_order_calls_api(self):
        self.bot.place_order("BTCUSDT", "Buy", 100, 10)
        self.session.set_leverage.assert_called_once_with(
            category="linear",
            symbol="BTCUSDT",
            buyLeverage="10",
            sellLeverage="10",
        )
        self.session.get_tickers.assert_called_once_with(
            category="linear", symbol="BTCUSDT"
        )
        self.session.place_order.assert_called_once()
        _, kwargs = self.session.place_order.call_args
        self.assertEqual(kwargs["category"], "linear")
        self.assertEqual(kwargs["symbol"], "BTCUSDT")
        self.assertEqual(kwargs["side"], "Buy")
        self.assertEqual(kwargs["orderType"], "Market")
        self.assertEqual(kwargs["timeInForce"], "ImmediateOrCancel")
        self.assertAlmostEqual(float(kwargs["qty"]), 10.0)

    def test_close_position_calls_api(self):
        self.bot.close_position("BTCUSDT", "Buy", 100, 10)
        self.session.place_order.assert_called_once()
        _, kwargs = self.session.place_order.call_args
        self.assertEqual(kwargs["category"], "linear")
        self.assertEqual(kwargs["symbol"], "BTCUSDT")
        self.assertEqual(kwargs["side"], "Sell")
        self.assertEqual(kwargs["orderType"], "Market")
        self.assertEqual(kwargs["timeInForce"], "ImmediateOrCancel")
        self.assertTrue(kwargs["reduceOnly"])
        self.assertAlmostEqual(float(kwargs["qty"]), 10.0)

    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.bot.place_order("BTCUSDT", "Buy", 70, 10)

    def test_invalid_leverage(self):
        with self.assertRaises(ValueError):
            self.bot.place_order("BTCUSDT", "Buy", 100, 5)

    def test_invalid_symbol(self):
        with self.assertRaises(ValueError):
            self.bot.place_order("ADAUSDT", "Buy", 100, 10)

    def test_invalid_position_value(self):
        with self.assertRaises(ValueError):
            self.bot.place_order("BTCUSDT", "Buy", 120, 11)

    def test_log_market_trend_increase(self):
        candles = [[0, 0, 0, 0, "110", 0]] + [[0, 0, 0, 0, "100", 0]] * 49
        self.session.get_kline.return_value = {"result": {"list": candles}}
        with self.assertLogs("bot", level="INFO") as cm:
            self.bot.log_market_trend("BTCUSDT")
        self.session.get_kline.assert_called_once_with(
            category="linear", symbol="BTCUSDT", interval=5, limit=50
        )
        self.assertIn("BTCUSDT: actively bought, price increases", cm.output[0])

    def test_log_market_trend_decrease(self):
        candles = [[0, 0, 0, 0, "90", 0]] + [[0, 0, 0, 0, "100", 0]] * 49
        self.session.get_kline.return_value = {"result": {"list": candles}}
        with self.assertLogs("bot", level="INFO") as cm:
            self.bot.log_market_trend("BTCUSDT")
        self.session.get_kline.assert_called_once_with(
            category="linear", symbol="BTCUSDT", interval=5, limit=50
        )
        self.assertIn("BTCUSDT: actively sold, price decreases", cm.output[0])

    def test_ma_crossover_signal_buy(self):
        candles = [[0, 0, 0, 0, "110", 0]] * 5 + [[0, 0, 0, 0, "100", 0]] * 45
        self.session.get_kline.return_value = {"result": {"list": candles}}
        signal = self.bot.ma_crossover_signal("BTCUSDT")
        self.assertEqual(signal, "Buy")

    def test_trade_with_ma_calls_place_order(self):
        candles = [[0, 0, 0, 0, "110", 0]] * 5 + [[0, 0, 0, 0, "100", 0]] * 45
        self.session.get_kline.return_value = {"result": {"list": candles}}
        self.bot.place_order = MagicMock()
        self.bot.trade_with_ma("BTCUSDT", 100, 10)
        self.bot.place_order.assert_called_once_with("BTCUSDT", "Buy", 100, 10)

    def test_place_order_ignores_leverage_error(self):
        self.session.set_leverage.side_effect = Exception(
            "leverage not modified (ErrCode: 110043)"
        )
        self.bot.place_order("BTCUSDT", "Buy", 100, 10)
        self.session.place_order.assert_called_once()


if __name__ == "__main__":
    unittest.main()
