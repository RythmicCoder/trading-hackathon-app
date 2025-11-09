import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import date, timedelta

# -------------------------------------------------
# Page Setup and Custom Theme
# -------------------------------------------------
st.set_page_config(page_title="Trading Strategy Dashboard", layout="wide")

# --- Inject Custom CSS for Styling ---
st.markdown("""
    <style>
        /* Background gradient */
        .stApp {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #f8f9fa;
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #111827;
            color: #f8f9fa;
        }

        /* Title */
        h1 {
            color: #00b4d8 !important;
            text-align: center;
        }

        /* Metric cards */
        div[data-testid="stMetricValue"] {
            color: #38bdf8 !important;
        }

        /* Buttons */
        button[kind="primary"] {
            background-color: #00b4d8 !important;
            color: white !important;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        button[kind="primary"]:hover {
            background-color: #0077b6 !important;
            color: #fff !important;
        }

        /* DataFrame table */
        div[data-testid="stDataFrame"] {
            background-color: #1e293b;
            border-radius: 8px;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.title("💹 Trading Strategy Dashboard")

# -------------------------------------------------
# Sidebar Inputs
# -------------------------------------------------
st.sidebar.header("Inputs")

default_tickers = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS"]
tickers = st.sidebar.multiselect("Select tickers", default_tickers, default=default_tickers[:2])

end_date = date.today()
start_date = end_date - timedelta(days=90)
start = st.sidebar.date_input("Start date", start_date)
end = st.sidebar.date_input("End date", end_date)

short_win = st.sidebar.number_input("Short SMA window", min_value=3, max_value=50, value=10, step=1)
long_win = st.sidebar.number_input("Long SMA window", min_value=10, max_value=200, value=30, step=1)
tx_cost_bps = st.sidebar.number_input("Transaction cost (bps per trade)", min_value=0, max_value=100, value=5, step=1)

take_profit = st.sidebar.number_input("Take Profit (%)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)
stop_loss = st.sidebar.number_input("Stop Loss (%)", min_value=0.0, max_value=50.0, value=3.0, step=0.5)

st.sidebar.caption("Tips: NSE tickers on Yahoo Finance end with .NS (e.g., TCS.NS)")

# -------------------------------------------------
# Fetch Prices (Cached)
# -------------------------------------------------
@st.cache_data(show_spinner=True)
def fetch_prices(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.rename(columns=str.title)
    return df

# -------------------------------------------------
# Build Signals
# -------------------------------------------------
def build_signals(prices, s_win, l_win):
    df = prices.copy()
    df["SMA_Short"] = df["Close"].rolling(s_win).mean()
    df["SMA_Long"] = df["Close"].rolling(l_win).mean()
    df["Signal"] = 0
    df.loc[df["SMA_Short"] > df["SMA_Long"], "Signal"] = 1
    df.loc[df["SMA_Short"] < df["SMA_Long"], "Signal"] = -1
    return df

# -------------------------------------------------
# Backtest Logic with Exit Rule
# -------------------------------------------------
def backtest(df, tx_cost_bps=5, take_profit=0.05, stop_loss=-0.03):
    if df.empty or "Signal" not in df.columns:
        return df, 0.0

    df = df.copy()
    df["Return"] = df["Close"].pct_change().fillna(0)
    df["Position"] = 0
    position = 0
    entry_price = None

    for i in range(1, len(df)):
        short_val = df["SMA_Short"].iloc[i]
        long_val = df["SMA_Long"].iloc[i]

        if pd.isna(short_val) or pd.isna(long_val):
            continue

        short = float(short_val)
        long = float(long_val)
        price = float(df["Close"].iloc[i])

        # Entry: Bullish crossover
        if position == 0 and short > long:
            position = 1
            entry_price = price

        # Exit: Bearish crossover or take-profit/stop-loss
        elif position == 1 and entry_price is not None:
            change = (price - entry_price) / entry_price
            if (short < long) or (change >= take_profit) or (change <= stop_loss):
                position = 0
                entry_price = None

        df.at[df.index[i], "Position"] = position

    df["Trade"] = df["Position"].diff().abs().fillna(0)
    tx_cost = (tx_cost_bps / 10000.0) * df["Trade"]
    df["StratRet"] = df["Position"].shift(1).fillna(0) * df["Return"] - tx_cost
    df["CumStock"] = (1 + df["Return"]).cumprod()
    df["CumStrat"] = (1 + df["StratRet"]).cumprod()

    total_pl = df["CumStrat"].iloc[-1] - 1 if len(df) > 0 else 0.0
    return df, total_pl

# -------------------------------------------------
# Run Backtest
# -------------------------------------------------
if st.sidebar.button("Run Backtest"):
    if not tickers:
        st.warning("Please select at least one ticker.")
    else:
        tabs = st.tabs(tickers)
        for i, t in enumerate(tickers):
            with tabs[i]:
                prices = fetch_prices(t, start, end)
                if prices.empty:
                    st.error(f"No data for {t}. Try another ticker or different dates.")
                    continue

                df = build_signals(prices, short_win, long_win)
                bt, pl = backtest(
                    df,
                    tx_cost_bps=tx_cost_bps,
                    take_profit=take_profit / 100,
                    stop_loss=-(stop_loss / 100)
                )

                st.subheader(f"{t} Results")
                st.metric("Total P/L (fractional)", f"{pl:.2%}")

                # Price + SMAs
                fig1, ax1 = plt.subplots()
                ax1.plot(bt.index, bt["Close"], label="Close")
                ax1.plot(bt.index, bt["SMA_Short"], label=f"SMA {short_win}")
                ax1.plot(bt.index, bt["SMA_Long"], label=f"SMA {long_win}")
                ax1.set_title(f"{t} Price with SMAs")
                ax1.legend()
                st.pyplot(fig1)

                # Equity Curves
                fig2, ax2 = plt.subplots()
                ax2.plot(bt.index, bt["CumStock"], label="Buy & Hold")
                ax2.plot(bt.index, bt["CumStrat"], label="Strategy")
                ax2.set_title(f"{t} Cumulative Returns")
                ax2.legend()
                st.pyplot(fig2)

                st.dataframe(bt[[
                    "Close", "SMA_Short", "SMA_Long", "Signal",
                    "Position", "Return", "StratRet", "CumStock", "CumStrat"
                ]].tail(20))

                # Download CSV Button
                csv_data = bt.to_csv(index=True).encode("utf-8")
                st.download_button(
                    label=f"📥 Download {t} Backtest Data as CSV",
                    data=csv_data,
                    file_name=f"{t}_backtest_results.csv",
                    mime="text/csv"
                )
else:
    st.info("Set your inputs in the sidebar and click 'Run Backtest'.")
