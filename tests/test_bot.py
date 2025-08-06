import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock

sys.path.append(str(Path(__file__).resolve().parents[1]))

from bot import BybitTradingBot


@pytest.fixture
def session():
    return MagicMock()


def test_place_order_calls_api(session):
    bot = BybitTradingBot(session)
    bot.place_order("BTCUSDT", "Buy", 100, 10)
    session.set_leverage.assert_called_once_with(
        category="linear",
        symbol="BTCUSDT",
        buyLeverage="10",
        sellLeverage="10",
    )
    session.place_order.assert_called_once_with(
        category="linear",
        symbol="BTCUSDT",
        side="Buy",
        orderType="Market",
        qty="1000",
        timeInForce="ImmediateOrCancel",
    )


def test_close_position_calls_api(session):
    bot = BybitTradingBot(session)
    bot.close_position("BTCUSDT", "Buy", 100, 10)
    session.place_order.assert_called_once_with(
        category="linear",
        symbol="BTCUSDT",
        side="Sell",
        orderType="Market",
        qty="1000",
        timeInForce="ImmediateOrCancel",
        reduceOnly=True,
    )


def test_invalid_amount(session):
    bot = BybitTradingBot(session)
    with pytest.raises(ValueError):
        bot.place_order("BTCUSDT", "Buy", 70, 10)


def test_invalid_leverage(session):
    bot = BybitTradingBot(session)
    with pytest.raises(ValueError):
        bot.place_order("BTCUSDT", "Buy", 100, 5)


def test_invalid_symbol(session):
    bot = BybitTradingBot(session)
    with pytest.raises(ValueError):
        bot.place_order("ADAUSDT", "Buy", 100, 10)
