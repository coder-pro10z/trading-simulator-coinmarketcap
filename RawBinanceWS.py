import asyncio
import websockets
import json
from datetime import datetime, timedelta


class BinanceWSClient:
    def __init__(self, symbol="btcusdt", runtime_minutes=3):
        self.symbol = symbol.lower()
        self.uri = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=runtime_minutes)
        self.balance = 100.0
        self.last_price = None
        self.trades = 0

    async def run(self):
        print(
            f"📡 Connecting to Binance WebSocket for {self.symbol} | Runtime: {self.end_time - self.start_time}"
        )
        async with websockets.connect(self.uri) as ws:
            while datetime.now() < self.end_time:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)

                    price = float(data["p"])
                    self.last_price = price
                    self.trades += 1
                    print(f"💰 Live Price: ${price:.2f}")

                    await asyncio.sleep(1)  # adjust as needed

                except Exception as e:
                    print(f"⚠️ Error: {e}")
                    break

        print(f"\n📊 Done. Total trades received: {self.trades}")
        print(f"📈 Last price seen: ${self.last_price:.2f}")


if __name__ == "__main__":
    asyncio.run(BinanceWSClient().run())
