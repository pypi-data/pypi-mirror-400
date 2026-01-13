from typing import *
from ...utils import *
from ...utils.legacy_utils import get_key_column_js
from abstract_utilities import make_list,SingletonMeta
class rowManager(metaclass=SingletonMeta):
    def __init__(self, 
                 txn_columns: Optional[List[str]] = None, 
                 main_columns: Optional[List[str]] = None, 
                 general_retain: Optional[List[str]] = None,
                 pools: Optional[List[str]] = None, 
                 pool_rows: Optional[List[str]] = None, 
                 pool_values: Optional[List[str]] = None,
                 pool_ids: Optional[List[str]] = None):
        if not hasattr(self, 'initialized'):
            self.initialized=True
            self.txn_columns = txn_columns
            self.main_columns = main_columns
            self.general_retain = general_retain
            self.pools = pools
            self.pool_rows = pool_rows
            self.pool_values = pool_values
            self.pool_ids = pool_ids
        
            self.reset()
    def reset(self,txn_columns: Optional[List[str]] = None, 
                 main_columns: Optional[List[str]] = None, 
                 general_retain: Optional[List[str]] = None,
                 pools: Optional[List[str]] = None, 
                 pool_rows: Optional[List[str]] = None, 
                 pool_values: Optional[List[str]] = None,
                 pool_ids: Optional[List[str]] = None):
        self.initialized=True
        
        self.txn_columns = txn_columns or self.txn_columns or [column for column in list(get_key_column_js().keys()) if 'virtual' not in column.lower()]
        self.main_columns = main_columns or self.main_columns or 'mint,name,symbol,orig#,txn#,sol_amount,timestamp,supply'.split(',')
        self.general_retain = general_retain or self.general_retain or []
        self.pools = pools or self.pools or pools or []
        self.pool_rows = pool_rows or self.pool_rows or []
        self.pool_values = pool_values or self.pool_values or []
        self.pool_ids = pool_ids or self.pool_ids or []
    def add_to_pools(self,pools = None,pool_rows = None,pool_data=None,pool_values = None,pool_ids = None):
        for pool in pools,pool_rows,pool_values,pool_ids:
            if pools:
                self.pools = pools
            if pool_rows:
                self.pool_rows = pool_rows
            if pool_values:
                self.pool_values = pool_values
            if pool_ids:
                self.pool_ids = pool_ids
            if pool_data:
                self.pool_data = pool_data

columns_mgr = rowManager()
def sift_key_values(dict_obj: Dict[str, Any], keys: List[str], out: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], List[str]]:
    """
    Attempt to extract the specified keys from dict_obj into the dictionary 'out'.
    Returns a tuple of (out, remaining_keys) where remaining_keys are those not found.
    """
    if out is None:
        out = {}
    remaining_keys = []
    dict_obj = if_list_get_single(dict_obj)

    for key in keys:
        if key not in out:
            out[key]=None
        value = dict_obj.get(key)
        if not value and key == 'timestamp':
            value = get_timestamps(dict_obj)
        if value:
            out[key] = value
        else:
            remaining_keys.append(key)
    return out, remaining_keys


def get_main_data_columns_from_row(row: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    Extracts main data columns from a single row by first checking the row itself
    and then (if needed) checking nested sub-dictionaries such as 'meta_data' and 'tcns'.
    
    Args:
        row: The input row as a dictionary.
        keys: A list of keys to look for (a copy of the master key list).
    
    Returns:
        A dictionary containing the found key-value pairs.
    """
    # Work on a copy of keys to avoid modifying the original list.
    remaining_keys = keys.copy()
    result: Dict[str, Any] = {}

    # First pass: extract from the main row dictionary.
    result, remaining_keys = sift_key_values(row, remaining_keys, result)
    if remaining_keys:
        # Second pass: if not all keys were found, try sub-dictionaries.
        for sub_field in ['meta_data', 'tcns']:
            if not remaining_keys:
                break  # All keys found; no need to continue.
            sub_objs = row.get(sub_field)
            for sub_obj in make_list(sub_objs):
                if sub_obj and isinstance(sub_obj, dict):
                    result, remaining_keys = sift_key_values(sub_obj, remaining_keys, result)
            # Optionally, if sub_obj might be a list of dictionaries, you could iterate over them.
    
    return result


def get_main_data_columns(rows: Any, main_columns: List[str]) -> List[Dict[str, Any]]:
    """
    Processes a collection of rows to extract main data columns based on the provided main_columns list.
    
    Args:
        rows: A single row or a list of rows.
        main_columns: The list of columns (keys) to extract.
    
    Returns:
        A list of dictionaries, each representing the extracted key-value pairs for a row.
    """
    pools: List[Dict[str, Any]] = []
    pool_rows: List[Dict[str, Any]] = []
    pool_values: List[Dict[str, Any]] = []
    pool_ids: List[Dict[str, Any]] = []
    pool_data: List[Dict[str, Any]] = []
    # Optionally, if you need to use ColumnsManager for more complex logic later,
    # you could initialize it here.
    columns_mgr.reset(general_retain=main_columns)
    
    for row in make_list(rows):
        row = dict(row)
        # Always work with a copy of the keys to avoid modifying the original list.
        pools.append(row)
        pool_id = get_main_data_columns_from_row(row,['pool_id'])
        pool_ids.append(pool_id.get('pool_id'))
        pool_data = get_main_data_columns_from_row(row, columns_mgr.general_retain.copy())
        pool_values.append(list(pool_data.values()))
        pool_rows.append(pool_data)
    columns_mgr.add_to_pools(pools = pools,pool_rows = pool_rows,pool_values = pool_values,pool_ids = pool_ids)
    return pools,pool_rows,pool_data,pool_values,pool_ids
