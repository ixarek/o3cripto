from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BybitConfig:
    api_key: str
    api_secret: str
    testnet: bool = False
    demo: bool = True
    ignore_ssl: bool = True

    @classmethod
    def from_env(cls) -> 'BybitConfig':
        return cls(
            api_key=os.getenv("BYBIT_API_KEY", ""),
            api_secret=os.getenv("BYBIT_API_SECRET", ""),
            testnet=os.getenv("BYBIT_TESTNET", "False").lower() == "true",
            demo=os.getenv("BYBIT_DEMO", "True").lower() == "true",
            ignore_ssl=os.getenv("BYBIT_IGNORE_SSL", "True").lower() == "true",
        )
