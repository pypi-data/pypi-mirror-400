from ...utils import *
def display_user_data(user_txns, user, txn_columns,window):
    """
    Display individual user's transaction data in the GUI.

    Parameters:
        user_data (dict): Data for the selected user.
        user (str): User address.
        window (sg.Window): The PySimpleGUI window.
    """
    #if user not in user_data:
    #    sg.popup_error(f"No data found for user: {user}")
    #    return
    txn_table_data = [[
        get_timestamps(txn),
        float(get_txn_price(txn) or 0),
        float(get_sol_amount(txn) or 0),
        float(get_token_amount(txn) or 0),
        "Buy" if get_is_buy(txn) else "Sell",
        get_signature(txn)
    ] for txn in user_txns]
    # Update table
    #window['-USER_TXN_TABLE-'].update(values=txn_table_data)
    window['-USER_TXN_TABLE-'].update(
                    values=[[function(txn) for function in [get_timestamps, get_txn_price, get_sol_amount, get_token_amount, get_is_buy, get_signature]] for txn in user_txns]
                )
    # Generate chart
    #chart_image_path = f"{user}_chart.png"

    #generate_price_chart(txn_table_data, save_path=chart_image_path)

    # Update chart display
    #window['-USER_CHART-'].update(filename=chart_image_path)

    # Update user-specific stats
    #user_stats = user_data[user]
    #window['-USER_STATS-'].update(
    #    f"User: {user}\n"
    #    f"Profit (SOL): {user_stats['profits']['sol']}\n"
    #    f"Average Price: {user_stats['avgPrice']['avg']}\n"
    #    f"Volume (Buy): {user_stats['volume']['buy']}\n"
    #    f"Volume (Sell): {user_stats['volume']['sell']}\n"
    #    f"Total Volume: {user_stats['volume']['total']}"
    #)
def set_user_info(txn_history,window):
    user_data = tally_profits(txn_history)
    user_wallets = list(user_data.keys())
    window['-USER_COMBO-'].update(values=user_wallets,value=user_wallets[0])
    return user_data
def tally_users(user_data,window,values):
    user_wallet = values['-USER_COMBO-'][0]
    display_user_data(user_data, user_wallet, window)
    #generate_price_chart(txn_history=user_txns['txns'],save_path="user_chart.png")
    #window['-USER_CHART-'].update(filename="user_chart.png")
