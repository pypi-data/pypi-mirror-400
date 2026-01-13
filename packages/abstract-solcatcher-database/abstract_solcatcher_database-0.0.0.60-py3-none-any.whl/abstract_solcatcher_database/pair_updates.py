import asyncio
import json
from datetime import datetime  # Import the datetime class directly.
import requests  # Consider replacing with aiohttp for async requests

from abstract_solcatcher import *
from abstract_utilities import *
from abstract_security import get_env_value
from abstract_apis import postRpcRequest, asyncPostRpcRequest, get_headers
from .db_funcs import get_pair, query_data

logger = get_logFile('pair_data')
PUMP_FUN_PROGRAMID = '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P'

fallback_url = 'https://rpc.ankr.com/solana/c3b7fd92e298d5682b6ef095eaa4e92160989a713f5ee9ac2693b4da8ff5a370'

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Custom dumps function using the above encoder
def custom_json_dumps(data):
    return json.dumps(data, cls=DateTimeEncoder)

def serialize_datetimes(obj):
    """
    Recursively converts datetime objects in a dict or list into ISO-formatted strings.
    """
    if isinstance(obj, dict):
        return {k: serialize_datetimes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetimes(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj

async def call_solcatcher_db(endpoint, **kwargs):
    # NOTE: Using requests.post in an async function is blocking.
    # Consider using aiohttp instead.
    response = requests.post(
        url=f'https://solcatcher.io/dbCalls/{endpoint}',
        data=json.dumps(kwargs),
        headers=get_headers()
    )
    response = get_response(response)
    if isinstance(response, dict):
        response = response.get('result', response)
    return response

async def fetch_transaction(signature):
    method = 'getTransaction'
    params = [signature, {"maxSupportedTransactionVersion": 0}]
    response = await asyncPostRpcRequest(
        url=fallback_url,
        method=method,
        params=params,
        response_result='result'
    )
    return response

async def fetch_signatures_from_address(address):
    method = 'getSignaturesForAddress'
    params = [address]
    response = await asyncPostRpcRequest(
        url=fallback_url,
        method=method,
        params=params,
        response_result='result'
    )
    return response

async def get_parsed_log_data(transaction):
    txn_data = {
        'signatures': get_any_value(transaction, 'signatures'),
        'slot': get_any_value(transaction, 'slot'),
        'signature': get_any_value(transaction, 'signatures')[0],
        'program_id': PUMP_FUN_PROGRAMID,
        'logs': get_any_value(transaction, 'logMessages')
    }
    return await async_call_solcatcher_ts('full-process-logs', **txn_data)

async def get_creation_pubkey(mint):
    meta_calls = ['get-or-fetch-metadata', 'fetch-meta']
    publickeys = None
    for call in meta_calls:
        metaData = await call_solcatcher_ts(call, mint=mint, url=fallback_url)
        if isinstance(metaData, int):
            metaData = await call_solcatcher_ts('get-or-fetch-metadata', mint=mint, url=fallback_url)
        publickeys = get_any_value(metaData, 'publicKey')
        if publickeys:
            break
    publickeys = [key for key in publickeys if key != mint] if publickeys else []
    return publickeys

async def decode_instruction_data(data):
    return await async_call_solcatcher_ts(endpoint='decode-instruction-data', data=data)

async def get_signatures_from_transaction(transaction):
    signatures = get_any_value(transaction, 'signatures')
    return signatures

async def get_creation_signature_from_mint(mint):
    addresses = await get_creation_pubkey(mint)
    if addresses:
        meta_address = addresses[0]
        sigs = await fetch_signatures_from_address(meta_address)
        signatures = [sig.get('signature') for sig in sigs]
        return signatures
    return None
async def get_transaction_from_signatures(signatures):
    transaction = await fetch_transaction(signature)

async def get_creation_transaction_from_mint(mint):
    signatures = await get_creation_signature_from_mint(mint)
    if signatures:
        signature = signatures[-1]
        transaction = await fetch_transaction(signature)
        return transaction,signature
    return None
async def get_creation_parsed_logs_from_mint(mint):
    transaction = await get_creation_transaction_from_mint(mint)
    logger.info(f"transaction = {transaction}")
    parsed_logs = await get_parsed_log_data(transaction)
    signatures = await get_signatures_from_transaction(transaction)
    for signature in signatures:
        log_data = await fetch_log_data(signature)
        if log_data:
            return signature, log_data
    return None, None

async def get_user_address(parsed_logs):
    if parsed_logs:
        logs = parsed_logs.get('logs', [])
        datas = [entry.get('data')[0] for entry in logs if entry.get('data') and 'Instruction: Create' in entry.get('logs', '')]
        for data in datas:
            if 'Instruction: Create' in data.get('logs', ''):
                raw_data = data.get('data')
                decoded_data = await decode_instruction_data(data=raw_data)
                user_address = decoded_data.get('user_address')
                return user_address
    return None
async def get_data_from_parsed_logs(parsed_logs):
    datas = []
    for entry in parsed_logs:
        if entry.get('data') and 'Instruction: Create' in entry.get('logs', ''):
            decoded = await decode_instruction_data(data=entry.get('data')[0])
            datas.append(decoded)
    return get_if_single(datas)
async def get_creation_instruction_data(mint):
    transaction = await get_creation_transaction_from_mint(mint=mint)
    parsed_logs = await get_parsed_log_data(transaction)
    return await get_data_from_parsed_logs(parsed_logs)
async def get_sanitized_pair(mint):
    pair = get_pair(mint=mint)
    while True:
        if pair and isinstance(pair,list) and len(pair) == 1:
            pair = pair[0]
        else:
            break
    pair = serialize_datetimes(pair)
    return pair
async def send_to_txn_queue(mint):
    pairMsg = {}
    transaction,signature = await get_creation_transaction_from_mint(mint=mint)
    pairMsg['signature']=signature
    pairMsg['logs'] = get_any_value(transaction,'logMessages')
    pairMsg['program_id'] = PUMP_FUN_PROGRAMID
    pairMsg['slot'] = get_any_value(transaction,'slot')
    await async_call_solcatcher_ts('sendTo-logIntake',**pairMsg);
    return signature
async def async_update_pair(mint):
    pair = await get_sanitized_pair(mint)
    transaction,signature = await get_creation_transaction_from_mint(mint=mint)
    pair['signature']=signature
    parsed_logs = await get_parsed_log_data(transaction)
    pair['log_id']=parsed_logs.get('log_id')
    decoded_data = await get_data_from_parsed_logs(parsed_logs.get('parsedLogs'))
    pair['user_address']=decoded_data.get('user_address')
    result = await async_call_solcatcher_ts('update-pair', pairData=pair)
    return pair
def update_pair(mint):
    return asyncio.run(async_update_pair(mint))

