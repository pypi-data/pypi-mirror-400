from ...utils.utils import get_sorted_txn_history,get_user_address,get_signature,get_sol_amount,get_token_amount
from abstract_utilities import make_list
def tally_profits(txns=None):
    """Organize and calculate profit, volume, and transaction data for each user."""
    txn_history = get_sorted_txn_history(txns)
    txnData_js = {}
    for txn in make_list(txn_history):
        user = get_user_address(txn)
        if isinstance(user,list):
            user = [use for use in user if use]
            if len(user)>0:
                user=user[0]
        for tx in make_list(txn):
            if user and user not in txnData_js:
                txnData_js[user] = {
                    "profits": {"sol": 0, "token": 0},
                    "avgPrice": {'token_amount': 0, 'sol': 0, "avg": 0},
                    "volume": {"sell": 0, "buy": 0, "total": 0},
                    "txns": []
                }
            solAmt = get_sol_amount(tx)
            tknAmt = get_token_amount(tx)
            txnData_js[user]["volume"]["total"] += solAmt

            if tx.get('isbuy'):
                txnData_js[user]["volume"]["buy"] += solAmt
                txnData_js[user]["profits"]["sol"] -= solAmt
            else:
                txnData_js[user]["volume"]["sell"] += solAmt
                txnData_js[user]["profits"]["sol"] += solAmt

            txnData_js[user]["avgPrice"]['token_amount'] += tknAmt
            txnData_js[user]["avgPrice"]['sol'] += solAmt
            # Avoid division by zero:
            token_amt = txnData_js[user]["avgPrice"]['token_amount'] or 1
            txnData_js[user]["avgPrice"]["avg"] = txnData_js[user]["avgPrice"]['sol'] / token_amt
            signature = get_signature(tx)
            txnData_js[user]["txns"].append(signature)
    return txnData_js
