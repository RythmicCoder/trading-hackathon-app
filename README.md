# Trading Hackathon Starter

## Quick start
1) Create and activate a virtual environment
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - macOS/Linux (bash/zsh):
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

2) Install packages
```bash
pip install -r requirements.txt
```

3) Run the app
```bash
streamlit run app.py
```

## What this does
- Lets you pick an NSE ticker (e.g., TCS.NS, INFY.NS, RELIANCE.NS).
- Pulls end-of-day data with `yfinance`.
- Builds a simple SMA crossover signal.
- Backtests the last 3 months by default.
- Shows charts and a profit summary.

## Notes
- For NSE stocks on Yahoo Finance, use the `.NS` suffix (e.g., "TCS.NS").
- This is a template; replace the strategy logic with what the problem statement needs.
