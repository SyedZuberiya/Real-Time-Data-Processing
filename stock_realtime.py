import asyncio
import websockets
import random
import json
import datetime
from collections import defaultdict, deque
import asyncpg  # async PostgreSQL client

# PostgreSQL connection details
PG_USER = "postgres"          # replace with your PostgreSQL username
PG_PASS = "Riya@123"          # replace with your PostgreSQL password
PG_DB = "tradedb"             # replace with your database name
PG_HOST = "localhost"
PG_PORT = 5432

# Sample stocks with initial prices
STOCKS = {
    "AAPL": 150.00,
    "GOOG": 2800.00,
    "TSLA": 720.00,
    "MSFT": 300.00
}

# Store price history for calculating changes
price_history = defaultdict(lambda: deque(maxlen=120))  # store last 120 seconds (2 mins)

# Store prices for averaging every 5 minutes (300 seconds)
price_5min = defaultdict(list)

# Track last alert old_price per symbol to prevent spamming alerts
last_alert_price = {}

async def mock_stock_server(websocket, path):
    try:
        while True:
            for symbol in STOCKS:
                # Simulate price change between -1% and +1%
                change_pct = random.uniform(-0.01, 0.01)
                STOCKS[symbol] *= (1 + change_pct)
                STOCKS[symbol] = round(STOCKS[symbol], 2)

                message = {
                    "symbol": symbol,
                    "price": STOCKS[symbol],
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
                await websocket.send(json.dumps(message))
                await asyncio.sleep(0.2)  # send updates quickly for demo
    except websockets.ConnectionClosed:
        print("Client disconnected")

async def notify_price_jump(pool, symbol, old_price, new_price):
    print(f"*** ALERT: {symbol} price jumped more than 2% in 1 minute! {old_price} -> {new_price}")
    # Save alert to DB
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO price_alerts (symbol, old_price, new_price, alert_time)
            VALUES ($1, $2, $3, $4)
        ''', symbol, old_price, new_price, datetime.datetime.utcnow())

async def save_average_price(pool, symbol, avg_price, timestamp):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO stock_averages (symbol, average_price, timestamp)
            VALUES ($1, $2, $3)
        ''', symbol, avg_price, timestamp)
    print(f"Saved average price for {symbol}: {avg_price} at {timestamp}")

async def stock_client():
    uri = "ws://localhost:8765"
    pool = await asyncpg.create_pool(user=PG_USER, password=PG_PASS, database=PG_DB, host=PG_HOST, port=PG_PORT)

    async with websockets.connect(uri) as websocket:
        while True:
            msg = await websocket.recv()
            data = json.loads(msg)
            symbol = data["symbol"]
            price = data["price"]
            timestamp = datetime.datetime.fromisoformat(data["timestamp"])

            # Store price for 1-minute price jump check
            price_history[symbol].append((timestamp, price))

            # Check price jump > 2% in last 1 minute
            prices = price_history[symbol]
            # Remove old prices beyond 1 minute
            cutoff = timestamp - datetime.timedelta(minutes=1)
            while prices and prices[0][0] < cutoff:
                prices.popleft()

            if prices:
                old_price = prices[0][1]
                if old_price > 0:
                    change_pct = (price - old_price) / old_price
                    if change_pct > 0.02:
                        # Check if alert already sent for this old_price
                        last_alert = last_alert_price.get(symbol)
                        if last_alert is None or last_alert != old_price:
                            await notify_price_jump(pool, symbol, old_price, price)
                            last_alert_price[symbol] = old_price
                    else:
                        # Reset alert if price falls below last alerted old_price
                        if symbol in last_alert_price:
                            if price < last_alert_price[symbol]:
                                del last_alert_price[symbol]

            # Collect prices for 5-minute averaging
            price_5min[symbol].append(price)

            # Every 5 minutes save average price
            # Assuming approx 0.2s per update, 1500 updates ~ 5 minutes
            if len(price_5min[symbol]) >= 1500:
                avg_price = round(sum(price_5min[symbol]) / len(price_5min[symbol]), 2)
                now = datetime.datetime.utcnow()
                await save_average_price(pool, symbol, avg_price, now)
                price_5min[symbol].clear()

async def main():
    print("Starting mock WebSocket server at ws://localhost:8765")
    server = await websockets.serve(mock_stock_server, "localhost", 8765)
    client_task = asyncio.create_task(stock_client())
    await client_task
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
