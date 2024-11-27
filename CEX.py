from dotenv import load_dotenv
import os
import time
import hmac
import hashlib
import requests

# Load environment variables
load_dotenv()

api_key = os.getenv("API_KEY").strip()
secret_key = os.getenv("SECRET_KEY").strip()

if not api_key or not secret_key:
    raise ValueError("API Key or Secret Key is missing.")
print("API Key and Secret Key successfully loaded!")

# MEXC Base API URL
base_url = "https://api.mexc.com"

# Headers for requests
headers = {
    "X-MEXC-APIKEY": api_key  # Correct header key
}

# Fetch ticker price (ETHUSDT)
ticker_endpoint = "/api/v3/ticker/price"
symbol = "ETHUSDT"
url = f"{base_url}{ticker_endpoint}?symbol={symbol}"

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print(f"Price of {symbol}: {data['price']}")
else:
    print(f"Failed to fetch price: {response.json()}")

# Authenticated endpoint: Account Info
account_info_endpoint = "/api/v3/account"
timestamp = int(time.time() * 1000)
params = f"timestamp={timestamp}&recvWindow=10000"  # Added recvWindow for flexibility
signature = hmac.new(secret_key.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()

url = f"{base_url}{account_info_endpoint}?{params}&signature={signature}"
print("Headers:", headers)  # Debug headers

response = requests.get(url, headers=headers)
if response.status_code == 200:
    print("Account Info:", response.json())
else:
    print(f"Failed to fetch account info: {response.json()}")

# Endpoint to place an order
order_endpoint = "/api/v3/order"
order_params = {
    "symbol": "ETHUSDT",  # Trading pair
    "side": "BUY",  # Buy order (use "SELL" for sell orders)
    "type": "MARKET",  # Market order (use "LIMIT" for limit orders)
    "quantity": 0.01,  # Quantity of ETH to buy
    "timestamp": int(time.time() * 1000),  # Timestamp
    "recvWindow": 10000  # Time window for the request (adjust as needed)
}

# Create query string and signature for the order
query_string = "&".join([f"{key}={value}" for key, value in order_params.items()])
signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
query_string += f"&signature={signature}"

url = f"{base_url}{order_endpoint}?{query_string}"

response = requests.post(url, headers=headers)

# Print the response for the order
if response.status_code == 200:
    print("Order placed successfully:", response.json())
else:
    print(f"Failed to place order: {response.json()}")

# Fetch open orders
open_orders_endpoint = "/api/v3/openOrders"
params = {
    "symbol": "ETHUSDT",
    "timestamp": int(time.time() * 1000),
    "recvWindow": 10000
}

query_string = "&".join([f"{key}={value}" for key, value in params.items()])
signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
query_string += f"&signature={signature}"

url = f"{base_url}{open_orders_endpoint}?{query_string}"

response = requests.get(url, headers=headers)
if response.status_code == 200:
    print("Open Orders:", response.json())
else:
    print(f"Failed to fetch open orders: {response.json()}")
markets_url = "https://api.mexc.com/api/v3/exchangeInfo"
response = requests.get(markets_url)
print(response.json())
