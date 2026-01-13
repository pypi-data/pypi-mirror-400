from abstract_solcatcher_database import *

ankr_url = 'https://rpc.ankr.com/solana/c3b7fd92e298d5682b6ef095eaa4e92160989a713f5ee9ac2693b4da8ff5a370'#await async_call_solcatcher_py('getUrl',method=method,solcatcherSettings=get_result_get_response)

def fetchmeta(mint):
    meta_data = asyncio.run(async_call_solcatcher_ts('get-metadata-foundation',mint=mint,url=ankr_url,get_id=False))
    
    return get_meta_data_from_meta_id(meta_data)
def get_or_fetch_meta(mint):
    meta_data = asyncio.run(async_call_solcatcher_ts('get-or-fetch-metadata',mint=mint))
    return meta_data
mint = 't4hHkXyRWmKgTG9ZthQXREVwTMwv8KGSw5c2xk1pump'
input(get_or_fetch_meta(mint=mint))
input(fetchmeta(mint=mint))
input(get_meta_data(mint=mint))
