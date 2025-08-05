from config import BybitConfig
from pybit.unified_trading import HTTP


def main() -> None:
    cfg = BybitConfig.from_env()
    session = HTTP(
        testnet=cfg.testnet,
        api_key=cfg.api_key,
        api_secret=cfg.api_secret,
        demo=cfg.demo,
        ignore_ssl=cfg.ignore_ssl,
    )
    print("Fetching account balance...")
    result = session.get_wallet_balance(accountType="UNIFIED")
    print(result)


if __name__ == "__main__":
    main()
