import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
import plotly.express as px

# ======================================
# CONFIG
# ======================================

DATA_FOLDER = "rsc_output"

st.set_page_config(layout="wide")
st.title("📊 Institutional Relative Strength Dashboard")

# ======================================
# LOAD DATA
# ======================================

@st.cache_data
def load_data(file):
    df = pd.read_csv(os.path.join(DATA_FOLDER, file))
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')
    return df

files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
index_names = [f.replace("_RSC.csv", "") for f in files]

# ======================================
# SIDEBAR
# ======================================

st.sidebar.header("Controls")

selected_indexes = st.sidebar.multiselect(
    "Select Indexes",
    index_names,
    default=index_names[:5]
)

timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["Daily", "Weekly", "Monthly"]
)

use_smoothing = st.sidebar.checkbox("Apply 20D Rolling Smoothing", True)
use_zscore = st.sidebar.checkbox("Use Z-Score Normalization", False)
show_heatmap = st.sidebar.checkbox("Show Heatmap", False)

start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# ======================================
# RESAMPLING
# ======================================

def resample_data(df, timeframe):

    if timeframe == "Daily":
        return df

    rule = "W" if timeframe == "Weekly" else "M"

    rsc = df['RSC'].resample(rule).mean()

    index_return = ((1 + df['Pct_Change']/100).resample(rule).prod() - 1) * 100
    benchmark_return = ((1 + df['Benchmark_Pct_Change']/100).resample(rule).prod() - 1) * 100

    result = pd.DataFrame({
        'RSC': rsc,
        'Pct_Change': index_return,
        'Benchmark_Pct_Change': benchmark_return
    })

    return result

# ======================================
# MAIN CHART
# ======================================

fig = go.Figure()
latest_values = {}

for idx in selected_indexes:

    df = load_data(idx + "_RSC.csv")
    df = df.loc[start_date:end_date]

    if df.empty:
        continue

    df_resampled = resample_data(df, timeframe)

    if df_resampled.empty:
        continue

    if use_smoothing:
        df_resampled['RSC'] = df_resampled['RSC'].rolling(20).mean()

    if use_zscore:
        mean = df_resampled['RSC'].mean()
        std = df_resampled['RSC'].std()
        df_resampled['RSC'] = (df_resampled['RSC'] - mean) / std

    latest_values[idx] = df_resampled['RSC'].iloc[-1]

    fig.add_trace(go.Scatter(
        x=df_resampled.index,
        y=df_resampled['RSC'],
        mode='lines',
        name=idx,
        customdata=np.stack(
            (df_resampled['Pct_Change'],
             df_resampled['Benchmark_Pct_Change']),
            axis=-1
        ),
        hovertemplate=
        "<b>%{fullData.name}</b><br>" +
        "Date: %{x}<br>" +
        "RSC: %{y:.4f}<br>" +
        "Index % Change: %{customdata[0]:.2f}%<br>" +
        "Benchmark % Change: %{customdata[1]:.2f}%<br>" +
        "<extra></extra>"
    ))

# Outperformance Highlight


fig.update_layout(
    height=700,
    template="plotly_dark",
    title="Relative Strength Comparative",
    yaxis_title="RSC",
    xaxis_title="Date"
)

st.plotly_chart(fig, use_container_width=True)

# ======================================
# RANKING TABLE
# ======================================

st.subheader("📈 Cross-Sectional Strength Ranking")

ranking_data = []

for idx in index_names:

    df = load_data(idx + "_RSC.csv")

    last_date = df.index.max()

    def window_return(days):
        recent = df[df.index >= last_date - pd.Timedelta(days=days)]
        return recent['RSC'].mean()

    ranking_data.append({
        "Index": idx,
        "1M": window_return(30),
        "3M": window_return(90),
        "6M": window_return(180),
        "12M": window_return(365)
    })

ranking_df = pd.DataFrame(ranking_data)
ranking_df = ranking_df.sort_values("3M", ascending=False)

st.dataframe(ranking_df, use_container_width=True)

# ======================================
# HEATMAP
# ======================================

if show_heatmap:

    st.subheader("🔥 Relative Strength Heatmap")

    latest_rsc = []

    for idx in index_names:
        df = load_data(idx + "_RSC.csv")
        latest_rsc.append(df['RSC'].iloc[-1])

    heat_df = pd.DataFrame({
        "Index": index_names,
        "Latest RSC": latest_rsc
    })

    heat_df = heat_df.sort_values("Latest RSC", ascending=False)

    fig2 = px.imshow(
        heat_df.set_index("Index").T,
        aspect="auto",
        color_continuous_scale="RdYlGn"
    )

    st.plotly_chart(fig2, use_container_width=True)