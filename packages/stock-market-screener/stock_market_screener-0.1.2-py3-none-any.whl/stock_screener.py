#!/usr/bin/env python3
"""
Stock Market Screener
A data-driven stock screener that analyzes Dow 30 stocks using technical indicators.
"""

import pandas as pd
import numpy as np
import yfinance as yf
import talib as ta
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configuration
START_DATE = '2025-01-01'
END_DATE = '2026-01-07'

# Dow 30 tickers
TICKERS = {
    "AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "DOW",
    "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM",
    "MRK", "MSFT", "NKE", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT"
}


def ma50_score(df):
    """
    Enhanced MA50 score:
    Combines % distance from MA50, short-term slope, and long-term trend filter.
    Score is normalized between -1 and +1.
    """
    ma50_series = ta.SMA(df['Close'], timeperiod=50)
    ma200_series = ta.SMA(df['Close'], timeperiod=200)

    ma50 = ma50_series.iloc[-1]
    ma50_5ago = ma50_series.iloc[-5]
    ma200 = ma200_series.iloc[-1]
    close = df['Close'].iloc[-1]

    # Distance from MA50 (capped)
    dist = (close - ma50) / ma50
    dist_score = max(-1, min(1, dist))

    # Slope of MA50 over last 5 periods
    slope = (ma50 - ma50_5ago) / ma50
    slope_score = max(-1, min(1, slope * 5))

    # Long-term regime
    regime = 1 if ma50 > ma200 else -1

    # Final score: combine all
    score = 0.5 * dist_score + 0.3 * slope_score + 0.2 * regime
    return max(-1, min(1, score))


def rsi_score_momentum(df, rsi_period=14, lookback=20):
    """
    Enhanced RSI momentum score:
    Measures recent RSI change normalized by 2x rolling std of RSI changes.
    Positive = RSI rising strongly, Negative = RSI falling strongly.
    Returns value between -1 and +1.
    """
    rsi_series = ta.RSI(df['Close'], timeperiod=rsi_period)
    rsi_change = rsi_series.diff()

    # Current change
    change = rsi_change.iloc[-1]
    # Rolling standard deviation of RSI changes
    stdev = rsi_change.rolling(lookback).std().iloc[-1]
    if pd.isna(stdev) or stdev == 0:
        return 0.0

    score = change / (2 * stdev)
    return max(-1, min(1, score))


def vol_score(df, lookback_vol=20, lookback_trend=5):
    """
    Enhanced volume score:
    Combines current volume ratio aligned with trend sign (50%)
    with short-term price slope normalized as trend strength (50%).
    """
    # Volume component
    avg_vol = df['Volume'].rolling(window=lookback_vol).mean().iloc[-1]
    curr_vol = df['Volume'].iloc[-1]
    ratio = curr_vol / avg_vol if avg_vol != 0 else 0
    ratio = min(ratio, 1.0)

    if df['Close'].iloc[-1] > df['Close'].iloc[-2]:
        trend_sign = 1
    elif df['Close'].iloc[-1] < df['Close'].iloc[-2]:
        trend_sign = -1
    else:
        trend_sign = 0
    
    score_volume = ratio * trend_sign
    return max(-1, min(1, score_volume))


def download_data(tickers, start_date, end_date):
    """Download historical data for tickers from Yahoo Finance."""
    print(f"Downloading data from {start_date} to {end_date}...")
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        group_by='ticker',
        auto_adjust=True,
        threads=True
    )
    return data


def calculate_scores(data, tickers):
    """Calculate scores for all tickers."""
    print("Calculating scores...")
    results = []

    for ticker in sorted(tickers):
        try:
            df_ticker = data[ticker][['Close', 'Volume']].dropna()
            result = {
                'Ticker': ticker,
                'ma50_score': ma50_score(df_ticker),
                'rsi_score': rsi_score_momentum(df_ticker),
                'vol_score': vol_score(df_ticker),
            }
            # Combine scores into a final score
            result['final_score'] = (result['ma50_score'] + result['rsi_score'] + result['vol_score']) / 3
            results.append(result)
        except Exception as e:
            print(f"Error calculating score for {ticker}: {e}")

    scanner_df = pd.DataFrame(results)
    return scanner_df


def plot_bar_chart(scanner_df):
    """Create a bar chart of final scores."""
    print("Creating bar chart...")
    plt.figure(figsize=(12, 6))
    scanner_df.plot(x='Ticker', y='final_score', kind='bar', legend=False, title='Final Score per Ticker')
    plt.tight_layout()
    plt.savefig('stock_screener_bar_chart.png', dpi=100, bbox_inches='tight')
    plt.show()


def plot_heatmap(scanner_df):
    """Create a heatmap visualization of scores."""
    print("Creating heatmap...")
    scores = scanner_df.copy().reset_index(drop=True)
    values = scores['final_score'].values

    # Determine grid size (approximately square)
    n = len(values)
    rows = int(np.ceil(np.sqrt(n)))
    cols = int(np.ceil(n / rows))

    grid = np.full((rows, cols), np.nan)
    labels = np.full((rows, cols), "", dtype=object)

    for i, val in enumerate(values):
        r = i // cols
        c = i % cols
        grid[r, c] = val
        labels[r, c] = scores['Ticker'].iloc[i]

    plt.figure(figsize=(10, 6))
    sns.heatmap(grid, annot=labels, fmt='', cmap='RdYlGn', center=0, cbar_kws={'label': 'Final Score'}, linewidths=0.5, linecolor='gray')
    plt.title('Stock Screener Heatmap')
    plt.yticks([])
    plt.xticks([])
    plt.savefig('stock_screener_heatmap.png', dpi=100, bbox_inches='tight')
    plt.show()


def save_results(scanner_df):
    """Save results to CSV."""
    filename = f'stock_screener_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    scanner_df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")
    return filename


def main():
    """Run the stock screener."""
    print("=" * 60)
    print("Stock Market Screener - Dow 30 Analysis")
    print("=" * 60)

    # Download data
    data = download_data(TICKERS, START_DATE, END_DATE)

    # Calculate scores
    scanner_df = calculate_scores(data, TICKERS)

    # Display results
    print("\nResults:")
    print(scanner_df.to_string())

    # Create visualizations
    plot_bar_chart(scanner_df)
    plot_heatmap(scanner_df)

    # Save results
    save_results(scanner_df)

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
