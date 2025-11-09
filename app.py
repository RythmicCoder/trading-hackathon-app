import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import date, timedelta

# -------------------------------------------------
# Streamlit Page Setup
# -------------------------------------------------
st.set_page_config(page_title="Trading Strategy Dashboard", layout="wide")

# --- Hide Streamlit Branding ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {visibility: hidden;}
        div[data-testid="stToolbar"] {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Sidebar Inputs
# -------------------------------------------------
st.sidebar.header("Dashboard Settings")

# Theme toggle
theme_choice = st.sidebar.radio(
    "Appearance",
    ["Dark Mode", "Light Mode"],
    index=0
)

# --- Dynamic Theme Styling ---
if theme_choice == "Dark Mode":
    st.markdown("""
        <style>
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            section[data-testid="stSidebar"] {
                background-color: #1c1f26;
                color: #fafafa;
            }
            h1 {
                color: #00b4d8 !important;
                text-align: center;
                font-weight: 600;
            }
            div[data-testid="stMetricValue"] { color: #00b4d8 !important; }
            button[kind="primary"] {
                background-color: #00b4d8 !important;
                color: white !important;
                border-radius: 6px;
            }
            div[data-testid="stDataFrame"] {
                background-color: #1f2937;
                border-radius: 8px;
                color: #fafafa;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            .stApp {
                background-color: #f4f6f8;
                color: #1e293b;
                font-family: "Inter", system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
            }
            section[data-testid="stSidebar"] {
                background-color: #ffffff;
                color: #1e293b;
                border-right: 1px solid #e2e8f0;
            }
            h1 {
                color: #005f99 !important;
                text-align: center;
                font-weight: 650;
                letter-spacing: 0.5px;
                margin-bottom: 1rem;
            }
            [data-testid="stWidgetLabel"], label, .stRadio label, .stSelectbox label,
            .stMultiSelect label, .stDateInput label, .stNumberInput label {
                color: #1e293b !important;
            }
            [data-testid="stNumberInput"] input,
            [data-testid="stDateInputInput"],
            div[data-baseweb="select"] > div,
            input, textarea, select {
                background-color: #ffffff !important;
                color: #111827 !important;
                border: 1px solid #d1d5db !important;
                border-radius: 6px !important;
            }
            div[data-baseweb="tag"] {
                background-color: #e7eef4 !important;
                color: #111827 !important;
            }
            ::placeholder { color: #6b7280 !important; }
            div[data-testid="stMetricValue"] { color: #0077b6 !important; font-weight: 600; }
            button[kind="primary"] {
                background-color: #0077b6 !important;
                color: #ffffff !important;
                border-radius: 6px;
                font-weight: 500;
                border: none;
                box-shadow: 0 2px 6px rgba(0,0,0,.08);
                transition: all .2s ease;
            }
            button[kind="primary"]:hover { background-color: #005f99 !important; }
            div[data-testid="stDataFrame"] {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
                color: #1e293b;
            }
            .stTabs [role="tablist"] { gap: 8px; }
            .stTabs [role="tab"] {
                background-color: #e7eef4;
                border-radius: 6px;
                padding: 6px 14px;
                color: #1e293b;
                font-weight: 500;
            }
            .stTabs [role="tab"][aria-selected="true"] {
                background-color: #0077b6;
                color: #ffffff;
            }
        </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# Title
# -------------------------------------------------
st.title("Trading Strategy Dashboard")

# -------------------------------------------------
# Sidebar Configuration
# -------------------------------------------------
default_tickers = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS"]
tickers = st.sidebar.multiselect("Select Stocks", default_tickers, default=default_tickers[:2])

end_date = date.today()
start_date = end_date - timedelta(days=90)
start = st.sidebar.date_input("Start Date", start_date)
end = st.sidebar.date_input("End Date", end_date)

ma_type = st.sidebar.selectbox("Moving Average Type", ["SMA", "EMA", "WMA"])
short_win = st.sidebar.number_input("Short MA Window", min_value=3, max_value=50, value=10, step=1)
long_win = st.sidebar.number_input("Long MA Window", min_value=10, max_value=200, value=30, step=1)
tx_cost_bps = st.sidebar.number_input("Transaction Cost (bps per trade)", min_value=0, max_value=100, value=5, step=1)
take_profit = st.sidebar.number_input("Take Profit (%)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)
stop_loss = st.sidebar.number_input("Stop Loss (%)", min_value=0.0, max_value=50.0, value=3.0, step=0.5)

st.sidebar.caption("Tip: Use Yahoo tickers ending with .NS for NSE stocks (e.g., TCS.NS)")

# -------------------------------------------------
# Fetch Prices
# -------------------------------------------------
def fetch_prices(ticker, start, end):
    # Add one day so the selected end date is included
    df = yf.download(ticker, start=start, end=end + timedelta(days=1))
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.rename(columns=str.title)
    return df


# -------------------------------------------------
# Build Signals (SMA / EMA / WMA)
# -------------------------------------------------
def build_signals(prices, s_win, l_win, ma_type="SMA"):
    df = prices.copy()
    if ma_type == "SMA":
        df["MA_Short"] = df["Close"].rolling(s_win).mean()
        df["MA_Long"] = df["Close"].rolling(l_win).mean()
    elif ma_type == "EMA":
        df["MA_Short"] = df["Close"].ewm(span=s_win, adjust=False).mean()
        df["MA_Long"] = df["Close"].ewm(span=l_win, adjust=False).mean()
    else:  # WMA
        weights_short = np.arange(1, s_win + 1)
        weights_long = np.arange(1, l_win + 1)
        df["MA_Short"] = df["Close"].rolling(s_win).apply(lambda x: np.dot(x, weights_short)/weights_short.sum(), raw=True)
        df["MA_Long"] = df["Close"].rolling(l_win).apply(lambda x: np.dot(x, weights_long)/weights_long.sum(), raw=True)

    df["Signal"] = 0
    df.loc[df["MA_Short"] > df["MA_Long"], "Signal"] = 1
    df.loc[df["MA_Short"] < df["MA_Long"], "Signal"] = -1
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
        short = float(df["MA_Short"].iloc[i]) if not pd.isna(df["MA_Short"].iloc[i]) else np.nan
        long = float(df["MA_Long"].iloc[i]) if not pd.isna(df["MA_Long"].iloc[i]) else np.nan
        price = float(df["Close"].iloc[i])

        if np.isnan(short) or np.isnan(long):
            continue

        # Entry: bullish crossover
        if position == 0 and short > long:
            position = 1
            entry_price = price

        # Exit: bearish crossover or take-profit/stop-loss
        elif position == 1 and entry_price is not None:
            change = (price - entry_price) / entry_price
            if (short < long) or (change >= take_profit) or (change <= stop_loss):
                position = 0
                entry_price = None

        df.at[df.index[i], "Position"] = position

    # Compute returns
    df["Trade"] = df["Position"].diff().abs().fillna(0)
    tx_cost = (tx_cost_bps / 10000.0) * df["Trade"]
    df["StratRet"] = df["Position"].shift(1).fillna(0) * df["Return"] - tx_cost
    df["CumStock"] = (1 + df["Return"]).cumprod()
    df["CumStrat"] = (1 + df["StratRet"]).cumprod()

    total_pl = df["CumStrat"].iloc[-1] - 1 if len(df) > 0 else 0.0
    return df, total_pl

# -------------------------------------------------
# Run Backtest Button
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

                df = build_signals(prices, short_win, long_win, ma_type)
                bt, pl = backtest(
                    df,
                    tx_cost_bps=tx_cost_bps,
                    take_profit=take_profit / 100,
                    stop_loss=-(stop_loss / 100)
                )

                st.subheader(f"{t} Results — {ma_type} Crossover")
                st.metric("Total P/L (fractional)", f"{pl:.2%}")

                fig1, ax1 = plt.subplots()
                ax1.plot(bt.index, bt["Close"], label="Close", linewidth=1.2)
                ax1.plot(bt.index, bt["MA_Short"], label=f"{ma_type} {short_win}", linewidth=1.1)
                ax1.plot(bt.index, bt["MA_Long"], label=f"{ma_type} {long_win}", linewidth=1.1)
                ax1.set_title(f"{t} Price with {ma_type}s")
                ax1.legend()
                st.pyplot(fig1)

                fig2, ax2 = plt.subplots()
                ax2.plot(bt.index, bt["CumStock"], label="Buy & Hold")
                ax2.plot(bt.index, bt["CumStrat"], label="Strategy")
                ax2.set_title(f"{t} Cumulative Returns")
                ax2.legend()
                st.pyplot(fig2)

                st.dataframe(bt[[
                    "Close", "MA_Short", "MA_Long", "Signal",
                    "Position", "Return", "StratRet", "CumStock", "CumStrat"
                ]].tail(20))

                csv_data = bt.to_csv(index=True).encode("utf-8")
                st.download_button(
                    label=f"Download {t} Backtest Data as CSV",
                    data=csv_data,
                    file_name=f"{t}_{ma_type}_backtest.csv",
                    mime="text/csv"
                )
else:
    st.info("Set your inputs in the sidebar and click 'Run Backtest'.")
