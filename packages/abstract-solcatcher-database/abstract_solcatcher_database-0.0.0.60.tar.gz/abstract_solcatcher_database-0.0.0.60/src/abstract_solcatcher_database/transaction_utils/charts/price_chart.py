import logging, os, json, time, requests
import pandas as pd
import mplfinance as mpf
from ...query_functions.call_functions import get_transactions
from ..user_txns.transaction_history import process_transaction_history
from ...utils import convert_chart_data_keys_to_int, get_timestamps, get_sorted_txn_history, get_txn_price, get_sol_amount, get_user_address, convert_timestamp_to_datetime

def generate_price_chart(txn_history=None, pair_id=None, save_path=None, highlight_user_address=None):
    """
    Generates a candlestick chart with volume indicators from transaction history, optionally highlighting a specific user's transactions.

    Parameters:
        txn_history (list of dict): The transaction history data for the entire pair.
        pair_id (str): The pair ID to fetch transactions if txn_history is not provided.
        save_path (str): Path to save the generated chart image.
        highlight_user_address (str, optional): The user address whose transactions should be highlighted.

    Returns:
        dict: Processed transaction data including chart data.
    """
    new_history = []
    if not txn_history and pair_id is not None:
        txn_history = get_transactions(pair_id=pair_id)
    elif isinstance(txn_history, int):
        txn_history = get_transactions(pair_id=txn_history)
    save_path = save_path or os.path.join(os.getcwd(), "chart.png")
    txn_history = get_sorted_txn_history(txn_history)

    # Debug: Check size of txn_history
    print(f"Total transactions in txn_history: {len(txn_history)}")

    # Step 1: Prepare transaction data
    for i, txn in enumerate(txn_history):
        if isinstance(txn, list):
            txn = txn[0]
        try:
            txn['timestamp'] = get_timestamps(txn)
            txn['price'] = get_txn_price(txn)
            txn['volume'] = get_sol_amount(txn)
            txn['user_address'] = get_user_address(txn)
            new_history.append(txn)
        except Exception as e:
            print(f"{e} and txn == {txn}")
    txn_history = new_history

    if not isinstance(txn_history, list) or not all(isinstance(item, dict) for item in txn_history):
        raise ValueError("txn_history must be a list of dictionaries with keys 'timestamp', 'price', and 'volume'.")

    # Step 2: Process and create DataFrame for the full pair chart
    processed_txns = process_transaction_history(txn_history)
    processed_txns['save_path'] = save_path
    processed_data = processed_txns.get('processed_data')

    try:
        df = pd.DataFrame(processed_data)
    except Exception as e:
        raise ValueError(f"Error creating DataFrame from transaction history: {e}")
    
    if df.empty:
        raise ValueError("DataFrame is empty after processing transaction history.")
    
    # Check for required columns
    required_columns = ['timestamp', 'price', 'volume']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in transaction history. Columns found: {df.columns.tolist()}")
    
    # Step 3: Ensure numeric columns
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    df.dropna(subset=['price', 'volume'], inplace=True)
    if df.empty:
        raise ValueError("DataFrame is empty after converting price and volume to numeric and dropping NaN values.")

    # Step 4: Convert timestamp to datetime and set as index
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce', utc=True)
    if df['datetime'].isnull().all():
        raise ValueError("All timestamps failed to convert. Check 'timestamp' column values.")
    df.set_index('datetime', inplace=True)
    df.sort_index(inplace=True)

    # Step 5: Resample DataFrame into OHLC and Volume for 1-minute intervals (full pair data)
    ohlc_dict = {'price': 'ohlc', 'volume': 'sum'}
    df_resampled = df.resample('1min').agg(ohlc_dict).dropna(how='any')
    if df_resampled.empty:
        raise print("No data available after resampling. Check if timestamps are too sparse.")
    
    print(f"Resampled data length: {len(df_resampled)}")

    # Step 6: Flatten multi-level columns and rename them for mplfinance
    df_resampled.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in df_resampled.columns]
    df_resampled.rename(columns={
        'price_open': 'Open', 
        'price_high': 'High', 
        'price_low': 'Low', 
        'price_close': 'Close', 
        'volume_volume': 'Volume'
    }, inplace=True)

    if 'Volume' not in df_resampled.columns:
        raise ValueError(f"'Volume' column is missing. Current columns: {df_resampled.columns}")

    # Step 7: Prepare data for highlighting the user's transactions
    user_txn_points = None
    if highlight_user_address:
        # Filter the original transaction history for the specific user
        user_txns = [txn for txn in txn_history if txn['user_address'] == highlight_user_address]
        print(f"User {highlight_user_address} transactions found: {len(user_txns)}")
        
        if user_txns:
            # Create a DataFrame for the user's transactions
            user_df = pd.DataFrame(user_txns)
            user_df['datetime'] = pd.to_datetime(user_df['timestamp'], unit='s', utc=True)
            user_df['price'] = pd.to_numeric(user_df['price'], errors='coerce')
            
            # Drop rows where price is NaN
            user_df.dropna(subset=['price'], inplace=True)
            if user_df.empty:
                print(f"Warning: No valid price data for user {highlight_user_address} after dropping NaN.")
            else:
                # Round user's timestamps to the nearest minute
                user_df['datetime_rounded'] = user_df['datetime'].dt.round('1min')
                
                # Group by rounded datetime and take the last price
                user_df = user_df.groupby('datetime_rounded')['price'].last().reset_index()
                user_df.set_index('datetime_rounded', inplace=True)
                
                # Reindex to match df_resampled.index
                user_df = user_df['price'].reindex(df_resampled.index, method=None)
                print(f"Reindexed user_df length: {len(user_df)}, df_resampled length: {len(df_resampled)}")
                print(f"User prices after reindexing: {user_df.tolist()}")
                
                # Check if there are any valid (non-NaN) prices
                if user_df.notna().any():
                    user_txn_points = mpf.make_addplot(
                        user_df,
                        type='scatter',
                        markersize=150,
                        marker='o',
                        color='yellow',
                        label=f"Trades by {highlight_user_address[:6]}...",
                        alpha=0.8
                    )
                else:
                    print(f"Warning: All user prices are NaN after reindexing. Skipping addplot.")

    try:
        # Step 8: Plot the candlestick chart with the full pair data and user highlights
        mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc)

        mpf.plot(
            df_resampled,  # Full pair OHLC data
            type='candle',
            style=s,
            volume=True,
            addplot=user_txn_points if user_txn_points else None,  # Overlay user's transactions
            savefig=dict(fname=save_path, format='png', bbox_inches='tight')
        )
        try:
            chart_data = df_resampled.to_dict()
                
            converted_chart_data_int = convert_chart_data_keys_to_int(chart_data)
            processed_txns['chart_data']=converted_chart_data_int
        except Exception as e:
            print(f"Error plotting candlestick chart: {e}")
    except Exception as e:
        raise print(f"Error plotting candlestick chart: {e}")
    print(f"Chart saved to {save_path}")
    return processed_txns
