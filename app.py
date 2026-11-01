import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import google.generativeai as genai

# Page Configuration for Mobile View
st.set_page_config(page_title="Quotex Real Market AI Bot", page_icon="📈", layout="centered")

st.title("🤖 Quotex Real-Data AI Signal Bot")
st.write("Fetching Live Market Data from Yahoo Finance for Real Price Action, RSI, MACD, Bollinger Bands & Wicks Analysis.")

# Input for Gemini API Key (Free from Google AI Studio)
gemini_api_key = st.text_input("Enter your Free Google AI Studio API Key", type="password")

# Mapping Quotex pairs to Yahoo Finance tickers
pair_mapping = {
    "EUR/USD (OTC)": "EURUSD=X",
    "GBP/USD (OTC)": "GBPUSD=X",
    "AUD/USD (OTC)": "AUDUSD=X",
    "USD/JPY (OTC)": "USDJPY=X",
    "EUR/JPY (OTC)": "EURJPY=X",
    "GBP/JPY (OTC)": "GBPJPY=X",
    "USD/CAD (OTC)": "USDCAD=X",
    "AUD/CAD (OTC)": "AUDCAD=X",
    "NZD/USD (OTC)": "NZDUSD=X",
    "EUR/GBP (OTC)": "EURGBP=X",
    "USD/CHF (OTC)": "USDCHF=X",
    "EUR/AUD (OTC)": "EURAUD=X",
    "CAD/JPY (OTC)": "CADJPY=X",
    "GBP/CHF (OTC)": "GBPCHF=X",
    "EUR/CAD (OTC)": "EURCAD=X",
    "AUD/NZD (OTC)": "AUDNZD=X",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "AUD/USD": "AUDUSD=X",
    "USD/JPY": "USDJPY=X",
    "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X",
    "USD/CAD": "USDCAD=X"
}

# User Controls
col1, col2 = st.columns(2)

with col1:
    currency_pair = st.selectbox("Choose Currency Pair / OTC", list(pair_mapping.keys()))

with col2:
    timeframe = st.selectbox("Choose Timeframe", ("1 Minute", "5 Minutes", "15 Minutes"))

st.markdown("---")

# Action Button to Get Signal based on Real Live Data
if st.button("🚀 Get Real-Data Candle Signal", type="primary", use_container_width=True):
    if not gemini_api_key:
        st.error("⚠️ Please enter your Gemini API Key first! (You can get it free from Google AI Studio)")
    else:
        with st.spinner("Fetching live market data & running deep AI analysis..."):
            try:
                ticker_symbol = pair_mapping[currency_pair]
                
                # Fetching real historical data from Yahoo Finance to calculate actual indicators
                interval_map = {"1 Minute": "1m", "5 Minutes": "5m", "15 Minutes": "15m"}
                df = yf.download(ticker_symbol, period="1d", interval=interval_map.get(timeframe, "1m"), progress=False)
                
                if df.empty or len(df) < 15:
                    st.error("⚠️ Could not fetch live data right now. Please try again.")
                else:
                    # Flatten columns if multi-index is returned by yfinance
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)

                    # Real Technical Calculations (RSI, Moving Averages, Volatility)
                    close_prices = df['Close']
                    delta = close_prices.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    rsi_series = 100 - (100 / (1 + rs))
                    current_rsi = float(rsi_series.iloc[-1])

                    # Bollinger Bands Calculation
                    sma_20 = close_prices.rolling(window=20).mean()
                    std_20 = close_prices.rolling(window=20).std()
                    upper_band = sma_20 + (std_20 * 2)
                    lower_band = sma_20 - (std_20 * 2)
                    
                    cur_close = float(close_prices.iloc[-1])
                    cur_upper = float(upper_band.iloc[-1])
                    cur_lower = float(lower_band.iloc[-1])
                    
                    # Candlestick Wicks & Body
                    cur_open = float(df['Open'].iloc[-1])
                    cur_high = float(df['High'].iloc[-1])
                    cur_low = float(df['Low'].iloc[-1])
                    
                    upper_wick = cur_high - max(cur_open, cur_close)
                    lower_wick = min(cur_open, cur_close) - cur_low
                    body_size = abs(cur_close - cur_open)

                    # Configure Gemini API
                    genai.configure(api_key=gemini_api_key)
                    model = genai.GenerativeModel('gemini-3.8-flash')
                    
                    # Comprehensive Prompt with REAL Calculated Market Data
                    prompt = f"""
                    You are an elite binary options trading AI expert specializing in real-time price action and indicator confluence.
                    Perform a rigorous multi-factor technical analysis using actual fetched market data for {currency_pair} ({ticker_symbol}) on {timeframe}:
                    - Current Market Price: {cur_close:.5f}
                    - Calculated Real RSI (14): {current_rsi:.2f}
                    - Bollinger Bands Upper: {cur_upper:.5f}, Lower: {cur_lower:.5f}
                    - Candlestick Metrics -> Open: {cur_open:.5f}, High: {cur_high:.5f}, Low: {cur_low:.5f}, Close: {cur_close:.5f}
                    - Body Size: {body_size:.5f}, Upper Wick: {upper_wick:.5f}, Lower Wick: {lower_wick:.5f}

                    Strict Evaluation Rules:
                    1. Base your decision strictly on the provided real market metrics and price action. No random assumptions.
                    2. You MUST give a clear, definitive direction for the next candle (CALL for Green, PUT for Red). No neutral or 'Wait' stances.
                    3. Calculate and provide an accurate confidence/strength percentage reflecting the exact reliability of this real setup.
                    
                    Give your output strictly in this professional format:
                    🎯 **Direction:** [CALL 🟢 (Green Candle Expected) OR PUT 🔴 (Red Candle Expected)]
                    💪 **Signal Strength:** [Percentage, e.g., 88%]
                    📉 **Technical Reason:** [Detailed breakdown explaining how real RSI, Wicks, Body, and Bollinger Bands led to this conclusion]
                    """

                    response = model.generate_content(prompt)
                    
                    st.markdown("### 📊 Real-Data Market Analysis & Signal:")
                    st.info(f"**Pair:** {currency_pair} | **Timeframe:** {timeframe} | **Live Price:** {cur_close:.5f}")
                    st.success(response.text)

            except Exception as e:
                st.error(f"An error occurred while fetching live data: {e}")
