# o3cripto

Simple Bybit futures trading bot example.

## Setup

1. Create a `.env` file based on `.env.example` and fill in your Bybit API credentials.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python bot.py
   ```

This example fetches and prints account balance using Bybit's demo environment.
It also provides helpers for placing and closing leveraged market orders on
`BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `XRPUSDT`, `DOGEUSDT` and `BNBUSDT`.

## Testing

Run unit tests with:

```bash
python -m unittest tests.test_bot
```
