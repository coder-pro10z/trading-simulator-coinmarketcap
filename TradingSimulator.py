# Here is a **fully modular trading simulator script** with:

# * ✅ `Strategy1`: Your original rules (5% loss, 10% profit, reinvest logic)
# * ✅ `Strategy2`: A more **aggressive** strategy (2% loss, 5% profit, etc.)
# * 🧠 Strategy selection is **automatic** for both — runs in parallel on same feed
# * 🕒 User can input **simulation runtime in minutes**
# * 🧾 Final summary for **both strategies separately**

# ---

# ### ✅ Modular Dual-Strategy Trading Simulator (Full Script)

# ---
import asyncio
import websockets
import json
from datetime import datetime, timedelta


# ---------- Strategy Base Interface ----------
class BaseStrategy:
    def __init__(self, name):
        self.name = name
        self.last_sell_price = None

    def on_price_update(self, price, context):
        """
        Should return: ('BUY' or 'SELL', reason: str) or (None, None)
        """
        raise NotImplementedError("Must implement on_price_update method")


# ---------- Strategy 1 ----------
class Strategy1(BaseStrategy):
    def __init__(self):
        super().__init__("Strategy1")
        self.sell_loss_threshold = 0.05
        self.sell_profit_threshold = 0.10
        self.reinvest_fall_threshold = 0.10
        self.buy_up_threshold = 0.03

    def on_price_update(self, price, context):
        if context["has_position"]:
            price_change_pct = (price - context["buy_price"]) / context["buy_price"]
            if price_change_pct <= -self.sell_loss_threshold:
                return "SELL", "5% Stop Loss"
            elif price_change_pct >= self.sell_profit_threshold:
                return "SELL", "10% Take Profit"
        else:
            if self.last_sell_price and price >= self.last_sell_price * (
                1 + self.buy_up_threshold
            ):
                return "BUY", "3% Recovery Buy"
            elif context["buy_price"] and price <= context["buy_price"] * (
                1 - self.reinvest_fall_threshold
            ):
                return "BUY", "10% Fall Reinvest"
        return None, None


# ---------- Strategy 2 (Aggressive Variant) ----------
class Strategy2(BaseStrategy):
    def __init__(self):
        super().__init__("Strategy2")
        self.sell_loss_threshold = 0.02
        self.sell_profit_threshold = 0.05
        self.reinvest_fall_threshold = 0.05
        self.buy_up_threshold = 0.02

    def on_price_update(self, price, context):
        if context["has_position"]:
            price_change_pct = (price - context["buy_price"]) / context["buy_price"]
            if price_change_pct <= -self.sell_loss_threshold:
                return "SELL", "2% Stop Loss"
            elif price_change_pct >= self.sell_profit_threshold:
                return "SELL", "5% Take Profit"
        else:
            if self.last_sell_price and price >= self.last_sell_price * (
                1 + self.buy_up_threshold
            ):
                return "BUY", "2% Recovery Buy"
            elif context["buy_price"] and price <= context["buy_price"] * (
                1 - self.reinvest_fall_threshold
            ):
                return "BUY", "5% Fall Reinvest"
        return None, None


# ---------- Simulator ----------
class TradingSimulator:
    def __init__(self, strategy, initial_investment=100.0, runtime_minutes=10):
        self.strategy = strategy
        self.name = strategy.name
        self.initial_investment = initial_investment
        self.runtime_minutes = runtime_minutes
        self.start_time = datetime.now()

        self.current_balance = initial_investment
        self.coin_holdings = 0.0
        self.buy_price = None
        self.has_position = False
        self.total_trades = 0
        self.profitable_trades = 0
        self.last_price = None

        print(
            f"📈 {self.name} Started | Runtime: {self.runtime_minutes} min | Initial: ${self.initial_investment}"
        )

    def should_stop(self):
        return datetime.now() - self.start_time >= timedelta(
            minutes=self.runtime_minutes
        )

    def calculate_coins(self, price):
        return self.current_balance / price

    def execute_buy(self, price, reason):
        if not self.has_position and self.current_balance > 0:
            coins = self.calculate_coins(price)
            self.coin_holdings = coins
            self.buy_price = price
            self.has_position = True
            self.current_balance = 0
            print(
                f"[{self.name}] 🟢 BUY at ${price:.4f} ({reason}) | Coins: {coins:.2f}"
            )

    def execute_sell(self, price, reason):
        if self.has_position:
            initial = self.coin_holdings * self.buy_price
            current = self.coin_holdings * price
            pnl = current - initial
            pnl_pct = (pnl / initial) * 100

            self.current_balance = current
            self.coin_holdings = 0
            self.has_position = False
            self.total_trades += 1
            if pnl > 0:
                self.profitable_trades += 1
            print(
                f"[{self.name}] 🔴 SELL at ${price:.4f} ({reason}) | P&L: {pnl:.2f} ({pnl_pct:+.2f}%)"
            )
            self.strategy.last_sell_price = price

    def on_price(self, price):
        self.last_price = price
        if self.should_stop():
            return False

        context = {
            "has_position": self.has_position,
            "buy_price": self.buy_price,
            "current_balance": self.current_balance,
        }

        action, reason = self.strategy.on_price_update(price, context)

        if action == "BUY":
            self.execute_buy(price, reason)
        elif action == "SELL":
            self.execute_sell(price, reason)
        return True

    def summary(self):
        print(f"\n📊 Summary for {self.name}")
        final_balance = self.current_balance
        if self.has_position and self.last_price:
            value = self.coin_holdings * self.last_price
            final_balance += value
            unrealized = value - (self.coin_holdings * self.buy_price)
            print(
                f"  Holding Coins: {self.coin_holdings:.2f} @ ${self.last_price:.4f} | Unrealized PnL: ${unrealized:.2f}"
            )
        pnl = final_balance - self.initial_investment
        pnl_pct = (pnl / self.initial_investment) * 100
        print(
            f"  Final Value: ${final_balance:.2f} | PnL: ${pnl:.2f} ({pnl_pct:+.2f}%)"
        )
        print(f"  Trades: {self.total_trades} | Wins: {self.profitable_trades}\n")


# ---------- WebSocket Client ----------
class WebSocketClient:
    def __init__(self, contract_address, runtime_minutes):
        self.uri = "wss://dws.coinmarketcap.com/ws"
        self.subscription = {
            "method": "SUBSCRIPTION",
            "params": [f"quote@transaction@16_{contract_address}"],
        }
        self.sim1 = TradingSimulator(Strategy1(), runtime_minutes=runtime_minutes)
        self.sim2 = TradingSimulator(Strategy2(), runtime_minutes=runtime_minutes)

    async def start(self):
        try:
            async with websockets.connect(self.uri) as ws:
                print("🔌 Connected to CoinMarketCap WebSocket")
                await ws.send(json.dumps(self.subscription))

                while True:
                    try:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        if "d" in data and "t0pu" in data["d"]:
                            price = float(data["d"]["t0pu"])
                            if not self.sim1.on_price(price) or not self.sim2.on_price(
                                price
                            ):
                                break
                    except Exception as e:
                        print(f"⚠️ Error: {e}")
                        break
        finally:
            self.sim1.summary()
            self.sim2.summary()


# ---------- Entry Point ----------
async def main():
    contract_address = input("📥 Enter contract address: ").strip()
    runtime_str = input("⏱️ Enter runtime in minutes: ").strip()

    if not contract_address:
        print("⚠️ Contract address required.")
        return
    try:
        runtime_minutes = int(runtime_str)
        client = WebSocketClient(contract_address, runtime_minutes)
        await client.start()
    except ValueError:
        print("⚠️ Invalid runtime value.")


if __name__ == "__main__":
    print("🎮 Dual-Strategy Crypto Trading Simulator")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Interrupted by user")


# ---

# ### 🧪 Example Run

# ```bash
# 🎮 Dual-Strategy Crypto Trading Simulator
# 📥 Enter contract address: 0x123...
# ⏱️ Enter runtime in minutes: 5
# ```

# Then it will:

# * Connect to CoinMarketCap WebSocket
# * Simulate both strategies side by side
# * Print trades and final summaries for both

# ---

# ### 📌 What You Can Do Next

# * Add `Strategy3`: e.g., RSI-based
# * Log trades to CSV for plotting
# * Backtest these strategies on historical price files
# * Visualize PnL using `matplotlib` or `plotly`

# Would you like me to show how to **backtest these strategies using CSV price data instead of WebSocket** for faster experiments?
