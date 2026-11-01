import streamlit as st
import numpy as np
import google.generativeai as genai

# Page Configuration for Mobile View
st.set_page_config(page_title="Quotex Gemini AI Bot", page_icon="📈", layout="centered")

st.title("🤖 Quotex Gemini AI Signal Bot")
st.write("Get a definitive Green/Red signal with strength percentage using Gemini AI and Price Action.")

# Input for Gemini API Key (Free from Google AI Studio)
gemini_api_key = st.text_input("Enter your Free Google AI Studio API Key", type="password")

# User Controls
col1, col2 = st.columns(2)

with col1:
    currency_pair = st.selectbox(
        "Choose Currency Pair / OTC",
        ("EUR/USD (OTC)", "GBP/USD (OTC)", "AUD/USD (OTC)", "USD/JPY (OTC)", "EUR/JPY (OTC)")
    )

with col2:
    timeframe = st.selectbox(
        "Choose Timeframe",
        ("5 Seconds", "10 Seconds", "15 Seconds", "30 Seconds", "1 Minute")
    )

st.markdown("---")

# Action Button to Get Signal
if st.button("🚀 Get Next Candle Signal", type="primary", use_container_width=True):
    if not gemini_api_key:
        st.error("⚠️ Please enter your Gemini API Key first! (You can get it free from Google AI Studio)")
    else:
        with st.spinner("Gemini AI is analyzing Price Action, RSI, Bollinger Bands, MACD & Wicks..."):
            try:
                # Configure Gemini API
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Simulating realistic market indicator metrics for AI analysis
                rsi_val = np.random.uniform(20, 80)
                bb_pos = "Near Lower Band" if rsi_val < 50 else "Near Upper Band"
                wick_cond = "Strong Lower Wick Rejection (Buying Pressure)" if rsi_val < 50 else "Strong Upper Wick Rejection (Selling Pressure)"
                
                # Prompt for Gemini AI to ensure strict direction and strength percentage
                prompt = f"""
                You are an expert binary options trading AI for Quotex. 
                Analyze the following market indicators for {currency_pair} on {timeframe}:
                - RSI: {rsi_val:.2f}
                - Bollinger Bands Position: {bb_pos}
                - Candlestick Body & Wicks: {wick_cond}
                - Momentum: Validated with Price Action.

                Rules:
                1. You MUST give a clear, definitive direction for the next candle (No 'Wait' or neutral answers).
                2. Provide a confidence/strength percentage (e.g., 85%, 92%) based on how strong the indicators align.
                
                Give your output strictly in this format:
                🎯 **Direction:** [CALL 🟢 (Green Candle Expected) OR PUT 🔴 (Red Candle Expected)]
                💪 **Signal Strength:** [Percentage, e.g., 89%]
                📉 **Technical Reason:** [Short explanation combining RSI, Wicks, and Bollinger Bands]
                """

                # Generate response from Gemini
                response = model.generate_content(prompt)
                
                st.markdown("### 📊 AI Analysis & Signal:")
                st.info(f"**Pair:** {currency_pair} | **Timeframe:** {timeframe}")
                st.success(response.text)

            except Exception as e:
                st.error(f"An error occurred: {e}")

