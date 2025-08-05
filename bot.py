from config import BybitConfig
from pybit.unified_trading import HTTP
import urllib3


def main() -> None:
    cfg = BybitConfig.from_env()

    session = HTTP(
        testnet=False if cfg.demo else cfg.testnet,
        api_key=cfg.api_key,
        api_secret=cfg.api_secret,
        demo=cfg.demo,
    )
    if cfg.ignore_ssl:
        session.client.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print("Fetching account balance...")
    try:
        response = session.get_wallet_balance(accountType="UNIFIED")
        if isinstance(response, tuple):
            response = response[0]
        if response.get("retCode") != 0:
            raise RuntimeError(response.get("retMsg", "Unknown error"))
    except Exception as exc:
        print(f"Failed to fetch balance: {exc}")
    else:
        print(response)


if __name__ == "__main__":
    main()
