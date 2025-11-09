# Trading Strategy Dashboard — Moving Average Crossover

An interactive **Streamlit dashboard** that visualizes **Moving Average (MA) crossover trading strategies** on real NSE stock data.
This project was developed as part of the **Trading Hackathon 2025** to analyze stock trends and generate **Buy / Sell / Hold** signals using end-of-day market prices.

---

##  Quick Start

### 1. Download or Clone the Repository
```bash
git clone https://github.com/RythmicCoder/trading-hackathon-app.git
cd trading-hackathon-app

2. Create a Virtual Environment (optional but recommended)
Windows:
python -m venv .venv
.venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Run the Application
streamlit run app.py

After running, the app will open automatically in your browser at:

http://localhost:8501

You can also use the Network URL (displayed in the terminal) to view the dashboard on another device connected to the same Wi-Fi network.
If hosted publicly on Streamlit Cloud, it can be accessed directly from a link like:https://trading-hackathon-app-ynwuo8hqggmxmy9w5zs38k.streamlit.app/
Data Source

The project uses the Yahoo Finance API through the yfinance Python package to fetch end-of-day (EOD) closing prices for NSE-listed stocks.
All data is publicly available and retrieved securely through the yf.download() method.

How It Works

Fetch Data:
Retrieves historical EOD data for selected stocks.

Calculate Moving Averages:
Computes short-term and long-term averages (SMA, EMA, or WMA).

Generate Signals:

BUY → Short-term MA crosses above long-term MA.

SELL → Short-term MA crosses below long-term MA.

HOLD → No crossover.

Backtest Strategy:
Simulates trades using your chosen parameters, applying transaction costs and stop-loss / take-profit logic.

Visualize Results:
Displays two charts — price vs. moving averages and cumulative returns — plus key performance metrics.

trading-hackathon-app/
│
├── app.py                # Main Streamlit app
├── requirements.txt      # Dependencies
├── README.md             # Documentation
