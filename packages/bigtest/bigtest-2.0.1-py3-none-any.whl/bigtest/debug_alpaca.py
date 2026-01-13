import requests
import os
import pandas as pd

# Keys provided by user
KEY_ID = "PK4VSDSWU2PWMUKPOFIMBHE2RO"
SECRET_KEY = "CJFG37tNUJbtrUwFyj67CoKswgGEf1deVweDpM7TfASn"

def test_alpaca_connection():
    print("--- Testing Alpaca Connection (Direct Requests) ---")
    
    # 1. Test Account (Paper API)
    print("\n1. Testing Trading API (Paper)...")
    url = "https://paper-api.alpaca.markets/v2/account"
    headers = {
        "APCA-API-KEY-ID": KEY_ID,
        "APCA-API-SECRET-KEY": SECRET_KEY
    }
    
    try:
        resp = requests.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("Account Info:", resp.json()['status'])
        else:
            print("Error:", resp.text)
    except Exception as e:
        print(f"Exception: {e}")

    # 2. Test Market Data (Data API)
    print("\n2. Testing Market Data API (v2)...")
    data_url = "https://data.alpaca.markets/v2/stocks/TSLA/bars"
    params = {
        "start": "2023-06-01T00:00:00Z",
        "end": "2023-06-02T00:00:00Z",
        "timeframe": "1Min",
        "limit": 10,
        "feed": "iex"
    }
    
    try:
        resp = requests.get(data_url, headers=headers, params=params)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Data received. Bars: {len(data.get('bars', []))}")
            if data.get('bars'):
                print("First bar:", data['bars'][0])
        else:
            print("Error:", resp.text)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_alpaca_connection()
