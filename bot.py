from config import BybitConfig
from pybit.unified_trading import HTTP
import urllib3


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

    def place_order(self, symbol: str, side: str, amount: float, leverage: int) -> dict:
        """Place a market order respecting risk limits."""
        self._validate(symbol, amount, leverage)
        qty = amount * leverage
        self.session.set_leverage(
            category="linear",
            symbol=symbol,
            buyLeverage=str(leverage),
            sellLeverage=str(leverage),
        )
        return self.session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=str(qty),
            timeInForce="ImmediateOrCancel",
        )

    def close_position(
        self, symbol: str, side: str, amount: float, leverage: int
    ) -> dict:
        """Close an existing position by placing an opposite market order."""
        self._validate(symbol, amount, leverage)
        qty = amount * leverage
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


def main() -> None:
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

    bot = BybitTradingBot(session)
    print("Fetching account balance...")
    try:
        result = session.get_wallet_balance(accountType="UNIFIED")
    except Exception as exc:
        print(f"Failed to fetch balance: {exc}")
    else:
        print(result)
    # Example usage (requires valid API keys):
    # bot.place_order("BTCUSDT", "Buy", 100, 10)
    # bot.close_position("BTCUSDT", "Buy", 100, 10)


if __name__ == "__main__":
    main()
