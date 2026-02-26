import os
import pandas as pd
import numpy as np

# =========================
# CONFIGURATION
# =========================

DATA_FOLDER = "index_data"
BENCHMARK_FILE = "Nifty 50_1D.csv"
START_DATE = "2024-01-01"
OUTPUT_FOLDER = "rsc_output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =========================
# LOAD BENCHMARK (NIFTY 50)
# =========================

benchmark_path = os.path.join(DATA_FOLDER, BENCHMARK_FILE)
benchmark_df = pd.read_csv(benchmark_path)

benchmark_df['time'] = pd.to_datetime(benchmark_df['time'])
benchmark_df = benchmark_df.sort_values('time')

# Filter from start date
benchmark_df = benchmark_df[benchmark_df['time'] >= START_DATE]

# Calculate % change of benchmark
benchmark_df['Benchmark_Pct_Change'] = benchmark_df['close'].pct_change() * 100

benchmark_df = benchmark_df[['time', 'Benchmark_Pct_Change']]

# =========================
# PROCESS ALL INDEX FILES
# =========================

for file in os.listdir(DATA_FOLDER):

    if not file.endswith(".csv"):
        continue

    if file == BENCHMARK_FILE:
        continue  # Skip Nifty 50

    print(f"Processing {file}...")

    file_path = os.path.join(DATA_FOLDER, file)
    df = pd.read_csv(file_path)

    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')

    # Filter from start date
    df = df[df['time'] >= START_DATE]

    # Calculate % change
    df['Pct_Change'] = df['close'].pct_change() * 100

    # Merge with benchmark
    merged_df = pd.merge(df, benchmark_df, on='time', how='left')

    # Calculate Relative Strength
    merged_df['RSC'] = np.where(
        merged_df['Benchmark_Pct_Change'] != 0,
        merged_df['Pct_Change'] / merged_df['Benchmark_Pct_Change'],
        np.nan
    )

    # Rearrange columns
    final_df = merged_df[
        ['time', 'open', 'high', 'low', 'close', 'volume',
         'Pct_Change', 'Benchmark_Pct_Change', 'RSC']
    ]

    # Save output
    output_filename = file.replace("_1D.csv", "_RSC.csv")
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    final_df.to_csv(output_path, index=False)

print("✅ All index RSC files generated successfully.")