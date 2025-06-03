# 🔌 Real-Time Stock Data Processing via WebSocket

This project simulates real-time stock data streaming using a WebSocket connection. It monitors stock price updates and triggers alerts based on price movements. Optionally, it calculates average prices every 5 minutes and stores them in a database.

---

## 🎯 Features

- **WebSocket Client:** Connects to a mock WebSocket server that emits simulated stock price updates.
- **Real-Time Alerts:** Detects and notifies when a stock's price increases by more than 2% within a single minute.
- **Bonus:** Calculates the average price for each stock every 5 minutes and stores it in a PostgreSQL or MongoDB database.

---

## ⚙️ Technologies Used

- Python 3.9+
- `websockets` – for WebSocket communication
- `asyncio` – for asynchronous real-time processing
- `pandas` – for time-series data manipulation
- `SQLAlchemy` or `pymongo` – for database interaction
- PostgreSQL or MongoDB (same as Task 1 database)

---

## 🔧 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/real-time-stock-ws.git
cd real-time-stock-ws
---
🧠 How It Works
The mock WebSocket server simulates live stock prices for multiple tickers.

The client connects to the server, receives JSON-formatted stock price messages like:
{
  "ticker": "AAPL",
  "price": 153.20,
  "timestamp": "2025-06-03T12:00:45"
}
---
For each ticker:

It tracks price changes over the past 60 seconds.

If the price increases by >2%, it prints/logs a notification.

Every 5 minutes, it calculates the average price and stores it in the database.
---
🔔 Example Notification
📈 ALERT: AAPL has increased by 2.4% in the last minute! (from $150.00 to $153.60)
---
Output
![image](https://github.com/user-attachments/assets/7418e5d6-bf4d-4009-b83c-b626ad5fc83b)
