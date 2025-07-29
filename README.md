# 🧠 trading-simulator-coinmarketcap

**A simple cryptocurrency trading simulator that uses real-time market data from Binance via WebSocket.**  
This project simulates buy/sell decisions based on customizable strategies, without risking real funds.

## 📁 Project Structure

```

trading-simulator-coinmarketcap
├─ config.json                # Strategy and simulation parameters
├─ RawBinanceWS.py           # Raw WebSocket data feed handler (Ping-Pong / KeepAlive included)
├─ TradingSimulator.py       # Main simulation engine with support for multiple strategies
├─ requirements.txt          # Python dependencies
└─ README.md                 # Project documentation (you're reading this)

````

---

## 🚀 Features

- 📈 Real-time data from Binance WebSocket
- 🧠 Plug-and-play trading strategies (customizable logic)
- 🧪 Paper trading simulation (no real orders placed)
- ⌛ Runtime-limited simulation
- 💰 Balance and net-worth tracking
- 🔁 Ping-Pong support to maintain live socket connection
- 🛠️ Easily extensible for new trading strategies

---

## 🧰 Requirements

- Python 3.8+
- Internet connection
- Basic understanding of trading concepts

Install dependencies:

```bash
pip install -r requirements.txt
````

---

## ⚙️ Configuration

Edit `config.json` to set up your simulation:

```json
{
  "ws_url": "wss://stream.binance.com:9443/ws",
  "symbol": "btcusdt",
  "runtime_minutes": 2,
  "initial_balance": 100,
  "strategies": [
    {
      "name": "SimplePriceTriggerStrategy",
      "threshold_percent": 0.2
    }
  ]
}
```

---

## ▶️ Running the Simulator

```bash
python TradingSimulator.py
```

Simulation output will show live prices, trades (buy/sell), and balance updates every second.

---

## 🧠 Strategies

### 1. SimplePriceTriggerStrategy

Buys when price increases by `+threshold_percent`, sells when price drops by `-threshold_percent`.

```python
self.start_price = 100
Price rises to 100.2 (+0.2%) → Simulated BUY
Price drops to 99.8 (-0.2%) → Simulated SELL
```

You can plug in additional strategy classes by extending the `TradingSimulator.py` and passing them in `config.json`.

---

## 📡 Raw WebSocket Data Tool

Use `RawBinanceWS.py` to inspect raw streaming trade data:

```bash
python RawBinanceWS.py
```

This is useful for debugging and validating live stream data.

---

## 🔄 Ping-Pong / KeepAlive

WebSocket keep-alive pings are handled automatically to avoid disconnects during simulations.

---

## 🛠️ Extending the Simulator

You can add more trading strategies by:

1. Creating a new class inside `TradingSimulator.py` or another strategy file.
2. Defining `should_buy(price)` and `should_sell(price)` methods.
3. Registering the strategy in the simulator via the `strategies` list in `config.json`.

---

## 🧪 Sample Output

```
📡 Connecting to wss://stream.binance.com:9443/ws/btcusdt@trade
💹 Price: $29482.43 | Balance: $100.00 | Holdings: 0.0000
🟢 Simulated BUY: 0.0034 BTC at $29490.00
🔴 Simulated SELL: 0.0034 BTC at $29585.00
📈 Net Worth: $101.59
```

---

## 📜 License

MIT License — Free for personal and commercial use.

---

## 💬 Contribution

Have a new strategy idea? Found a bug?
Feel free to open an issue or submit a pull request!

---

## 🤝 Acknowledgements

* [Binance WebSocket API](https://binance-docs.github.io/apidocs/spot/en/#websocket-market-streams)
* [Python WebSocket Client](https://pypi.org/project/websockets/)
* Community contributions and feedback

```
