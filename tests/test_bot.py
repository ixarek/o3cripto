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
        self.bot = BybitTradingBot(self.session)

    def test_place_order_calls_api(self):
        self.bot.place_order("BTCUSDT", "Buy", 100, 10)
        self.session.set_leverage.assert_called_once_with(
            category="linear",
            symbol="BTCUSDT",
            buyLeverage="10",
            sellLeverage="10",
        )
        self.session.place_order.assert_called_once_with(
            category="linear",
            symbol="BTCUSDT",
            side="Buy",
            orderType="Market",
            qty="1000",
            timeInForce="ImmediateOrCancel",
        )

    def test_close_position_calls_api(self):
        self.bot.close_position("BTCUSDT", "Buy", 100, 10)
        self.session.place_order.assert_called_once_with(
            category="linear",
            symbol="BTCUSDT",
            side="Sell",
            orderType="Market",
            qty="1000",
            timeInForce="ImmediateOrCancel",
            reduceOnly=True,
        )

    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.bot.place_order("BTCUSDT", "Buy", 70, 10)

    def test_invalid_leverage(self):
        with self.assertRaises(ValueError):
            self.bot.place_order("BTCUSDT", "Buy", 100, 5)

    def test_invalid_symbol(self):
        with self.assertRaises(ValueError):
            self.bot.place_order("ADAUSDT", "Buy", 100, 10)


if __name__ == "__main__":
    unittest.main()
