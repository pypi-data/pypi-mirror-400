import logging,os,json,time,requests
from abstract_utilities import make_list
from datetime import datetime
from ...utils.utils import (
    get_txn_price,
    get_virtual_token_reserves,
    get_virtual_sol_reserves,
    get_token_amount,
    get_sol_amount,
    get_sorted_txn_history,
    get_user_address,
    get_signature,
    get_timestamps,
    get_is_buy,
    if_list_get_single,
    get_mint,
    get_bonding_curve,
    get_string_value
    )
from ...query_functions.call_functions import get_creation_decoded_data,get_pair
def process_transaction_history(txn_history=None,pair_id=None):
    """
    Processes a list of transaction history and returns a cleaned, structured list of transactions
    with Unix timestamps and other essential data.

    Args:
    txn_history (list): List of transaction dictionaries.

    Returns:
    tuple: A tuple containing:
        - processed_data (list): The cleaned list of transactions.
        - init_sol_amount (float): Initial SOL amount.
        - init_token_amount (float): Initial token amount.
        - init_virtualSolReserves (int): Initial virtual Sol reserves.
        - init_virtualTokenReserves (int): Initial virtual token reserves.
        - init_price (float): Initial price derived from virtual reserves.
    """
    processed_data = []
    init_sol_amount = 0
    init_token_amount = 0
    init_virtualSolReserves = 0
    init_virtualTokenReserves = 0
    init_price = 0
    txn_history = get_sorted_txn_history(txn_history)
    if len(txn_history)>0:
        initial_txn = txn_history[0]
    else:
        return None
    pair_id = pair_id or initial_txn.get('pair_id')
    if not pair_id:
        signature = get_signature(txn_history[0])
        pair = get_pair(signature=signature)
        pair = if_list_get_single(pair)
        pair_id = get_string_value(pair,'id')
    pair = get_pair(pair_id = pair_id)
    creator_address = get_user_address(pair)
    if not creator_address:
        pair = get_creation_decoded_data(pair_id = pair_id)
        creator_address = get_user_address(pair)
    # If txn_history is a tuple of lists, flatten it
    mint = get_mint(pair)
    bonding_curve = get_bonding_curve(pair)
    if txn_history:
        # Extract initialization parameters from the first transaction
        init_txn = txn_history[0]
        init_sol_amount = get_sol_amount(init_txn)
        init_token_amount = get_token_amount(init_txn)
        init_virtualSolReserves = get_virtual_sol_reserves(init_txn)
        init_virtualTokenReserves = get_virtual_token_reserves(init_txn)  # Avoid division by zero
        init_price = get_txn_price(init_txn)
    for txn in txn_history:
        try:
            typ = 'Buy' if get_is_buy(txn) else 'Sell'
            sol_amount = get_sol_amount(txn)
            token_amount = get_token_amount(txn)
            price = get_txn_price(txn)
            # Extract and convert timestamp to Unix time
            timestamp = get_timestamps(txn)
            if isinstance(timestamp, str):
                try:
                    # Check for multiple formats of the timestamp
                    if ',' in timestamp:  # RFC 1123 format
                        readable_time = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %Z')
                    else:  # ISO 8601 format
                        readable_time = datetime.fromisoformat(timestamp)
                    unix_timestamp = int(readable_time.timestamp())
                except Exception as e:
                    logging.error(f"Error converting timestamp from string '{timestamp}': {e}")
                    unix_timestamp = 0
            elif isinstance(timestamp, (int, float)):  # If it's already a numeric timestamp
                unix_timestamp = int(timestamp)
            else:
                logging.error(f"Unsupported timestamp type for value '{timestamp}'")
                unix_timestamp = 0

            processed_data.append({
                'type': typ,
                'timestamp':timestamp,   # Store the Unix timestamp directly
                'price': f"{price:.9f}",
                'sol_amount': f"{sol_amount:.9f}",
                'volume': f"{sol_amount:.9f}",
                'user_address':get_user_address(txn),
                'token_amount': f"{token_amount:.9f}",
                'signature': get_signature(txn),
                'unix_timestamp':unix_timestamp,
                
            })

        except Exception as e:
            logging.error(f"Error processing transaction: {txn}, error: {e}")
            continue
    transaction_history = {
                "processed_data": processed_data,
                "init_sol_amount": init_sol_amount,
                "init_token_amount": init_token_amount,
                "init_virtualSolReserves": init_virtualSolReserves,
                "init_virtualTokenReserves": init_virtualTokenReserves,
                "init_price": init_price,
                "mint":mint,
                "creator_address":creator_address,
                "bonding_curve":bonding_curve
            }
    return transaction_history
