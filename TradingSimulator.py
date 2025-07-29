import asyncio
import json
from datetime import datetime, timedelta
import websockets


# === STRATEGY CLASSES ===
class SimplePriceTriggerStrategy:
    def __init__(self, threshold_percent=0.2, name="StrategyA"):
        self.start_price = None
        self.threshold_percent = threshold_percent
        self.name = name

    def should_buy(self, current_price):
        if self.start_price is None:
            self.start_price = current_price
            return False
        change = ((current_price - self.start_price) / self.start_price) * 100
        return change >= self.threshold_percent

    def should_sell(self, current_price):
        if self.start_price is None:
            return False
        change = ((self.start_price - current_price) / self.start_price) * 100
        return change >= self.threshold_percent


# === TRADER SIMULATOR CLASS ===
class TradingSimulator:
    def __init__(
        self, ws_url, symbol="btcusdt", runtime_minutes=2, initial_balance=100.0
    ):
        self.symbol = symbol
        self.uri = f"{ws_url}/{symbol.lower()}@trade"
        self.end_time = datetime.now() + timedelta(minutes=runtime_minutes)
        self.balance = initial_balance
        self.holdings = 0
        self.last_price = None

        # === Add multiple strategies ===
        self.strategies = [
            SimplePriceTriggerStrategy(threshold_percent=0.2, name="Aggressive"),
            SimplePriceTriggerStrategy(threshold_percent=1.0, name="Conservative"),
        ]

    async def run(self):
        print(f"📡 Connecting to {self.uri}")
        async with websockets.connect(self.uri, ping_interval=10, ping_timeout=5) as ws:
            ping_task = asyncio.create_task(self._send_ping(ws))
            try:
                while datetime.now() < self.end_time:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=15)
                        data = json.loads(message)
                        price = float(data["p"])
                        self.last_price = price
                        self.evaluate_strategies(price)
                        await asyncio.sleep(1)
                    except asyncio.TimeoutError:
                        print("⚠️ Timeout waiting for message.")
                        break
                    except Exception as e:
                        print(f"⚠️ Error: {e}")
                        break
            finally:
                ping_task.cancel()

        self.summary()

    async def _send_ping(self, ws):
        while True:
            try:
                await asyncio.sleep(15)
                await ws.ping()
                print("📶 Sent ping")
            except Exception as e:
                print(f"⚠️ Ping error: {e}")
                break

    def evaluate_strategies(self, price):
        print(
            f"\n💹 Price: ${price:.2f} | Balance: ${self.balance:.2f} | Holdings: {self.holdings:.4f}"
        )

        for strategy in self.strategies:
            print(f"🧠 Evaluating {strategy.name}")
            if strategy.should_buy(price) and self.balance > 0:
                qty = self.balance / price
                self.holdings += qty
                print(
                    f"🟢 [{strategy.name}] BUY: {qty:.4f} {self.symbol.upper()} at ${price:.2f}"
                )
                self.balance = 0

            elif strategy.should_sell(price) and self.holdings > 0:
                self.balance += self.holdings * price
                print(
                    f"🔴 [{strategy.name}] SELL: {self.holdings:.4f} {self.symbol.upper()} at ${price:.2f}"
                )
                self.holdings = 0

    def summary(self):
        net_worth = self.balance + (
            self.holdings * self.last_price if self.holdings else 0
        )
        print("\n📊 Simulation Finished:")
        print(f"💵 Final Balance: ${self.balance:.2f}")
        print(f"📦 Final Holdings: {self.holdings:.4f}")
        print(f"💰 Last Price: ${self.last_price:.2f}")
        print(f"📈 Net Worth: ${net_worth:.2f}")


# === MAIN ===
if __name__ == "__main__":
    BINANCE_WS = "wss://stream.binance.com:9443/ws"
    simulator = TradingSimulator(ws_url=BINANCE_WS, symbol="btcusdt", runtime_minutes=2)
    asyncio.run(simulator.run())
