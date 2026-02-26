import os
import time
import pandas as pd
from datetime import datetime, timedelta
from fyers_apiv3 import fyersModel

CLIENT_ID = "41THCFG0AZ-100"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIl0sImF0X2hhc2giOiJnQUFBQUFCcG9FSmQyd1NpUk9renoyVC1ZeHZQMmtGX2FiMzIzQ3AzTWJ6T29BN0N6MURLNnA0aE9sbjJfRS1wZ04zN0Z0eW9WOTFyMEVXT3htd044LVFFN3M2NHdtVU9iUnM2UGxVYVE4SGc2SlJ2UXJGRkRpYz0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiJlZmQ1NTk4M2IyMDA5ZDg3ZmMxZmJjYTViZDk2MWI5MzJiOGI0OGE0OTEwZjkxZDVjN2MzMDZiNiIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiRkFENzgwMTYiLCJhcHBUeXBlIjoxMDAsImV4cCI6MTc3MjE1MjIwMCwiaWF0IjoxNzcyMTEwNDI5LCJpc3MiOiJhcGkuZnllcnMuaW4iLCJuYmYiOjE3NzIxMTA0MjksInN1YiI6ImFjY2Vzc190b2tlbiJ9.72jDdjjwj033c0x4h0_kapfQWlzfD-kPBR45X5aYtSM"

fyers = fyersModel.FyersModel(
    client_id=CLIENT_ID,
    is_async=False,
    token=ACCESS_TOKEN,
    log_path=""
)

OUTPUT_DIR = "index_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=1000)

def to_epoch(dt):
    return int(dt.timestamp())

def date_chunks(start, end, days=100):
    chunks = []
    current = start
    while current < end:
        nxt = min(current + timedelta(days=days), end)
        chunks.append((current, nxt))
        current = nxt
    return chunks

def sanitize_filename(filename):
    """Replace invalid filename characters with underscores"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def load_indices_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    indices = {}
    
    for _, row in df.iterrows():
        if row['Status'] == 'Matched' and str(row['API Sysname']).strip() != 'nan':
            api_sysname = row['API Sysname']
            index_name = row['IndexName']
            indices[api_sysname] = index_name
    
    return indices

def fetch_history(api_sysname, index_name, resolution):
    print(f"\n📥 Fetching {resolution} data for {index_name}")

    all_candles = []

    for start, stop in date_chunks(START_DATE, END_DATE):
        payload = {
            "symbol": api_sysname,
            "resolution": resolution,
            "date_format": "0",
            "range_from": str(to_epoch(start)),
            "range_to": str(to_epoch(stop)),
            "cont_flag": "1"
        }

        try:
            res = fyers.history(data=payload)
            if res.get("s") == "ok" and "candles" in res:
                all_candles.extend(res["candles"])
            else:
                print(f"⚠️ Skipped {start.date()} → {stop.date()}")
        except Exception as e:
            print(f"❌ Error: {e}")

        time.sleep(0.5)

    if not all_candles:
        print(f"⚠️ No data fetched for {index_name}")
        return

    df = pd.DataFrame(
        all_candles,
        columns=["epoch", "open", "high", "low", "close", "volume"]
    )

    df = df.drop_duplicates(subset=["epoch"], keep="last")
    df = df.sort_values("epoch").reset_index(drop=True)

    df["time"] = pd.to_datetime(df["epoch"], unit="s", utc=True)

    if resolution == "60":
        df["time"] = df["time"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    elif resolution == "1D":
        df["time"] = df["time"].dt.tz_convert("Asia/Kolkata").dt.date

    df = df[["time", "open", "high", "low", "close", "volume"]]

    sanitized_name = sanitize_filename(index_name)
    file_name = f"{sanitized_name}_{resolution}.csv"
    out_path = os.path.join(OUTPUT_DIR, file_name)
    df.to_csv(out_path, index=False)

    print(f"✅ Saved → {out_path}")

if __name__ == "__main__":
    indices = load_indices_from_csv("matching_results.csv")
    print(f"✅ Loaded {len(indices)} indices\n")
    
    timeframes = ["1D"]
    
    print(f"📅 Fetching data from {START_DATE.date()} to {END_DATE.date()}\n")

    for idx, (api_sysname, index_name) in enumerate(indices.items(), 1):
        print(f"\n[{idx}/{len(indices)}] {index_name}")
        for tf in timeframes:
            fetch_history(api_sysname, index_name, tf)