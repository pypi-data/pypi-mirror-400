import logging

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set level to INFO or higher
from psycopg2 import sql, connect
from psycopg2.extras import DictCursor
from abstract_utilities import make_list, SingletonMeta, is_number
from abstract_security import get_env_value
import psycopg2,time
from .connect import get_connection
env_path = '/home/solcatcher/.env'

def get_env_val(key):
    return get_env_value(key=key, path=env_path)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def get_all_table_names(schema='public'):
    """Fetch all table names from a specified schema."""
    conn = get_connection()
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s AND table_type = 'BASE TABLE';
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (schema,))
            table_names = [row[0] for row in cursor.fetchall()]
            return table_names
    except Exception as e:
        print(f"An error occurred in get all tyables: {e}")
    finally:
        conn.close()
def get_time_interval(seconds =0,minutes=0, hours=0, days=0, weeks=0,months=0, years=0,*args,**kwargs):
    """Calculate a UNIX timestamp for the given time offset."""
    secs = 1
    mins = secs*60
    hr = 60 * mins
    day = 24 * hr
    week = 7 * day
    year = 365 * day
    month = year/12
    return ((secs * seconds) + (mins * minutes) + (hr * hours) + (day * days) + (week * weeks) + (month * months) + (year * years))

def get_time(time_interval,*args,**kwargs):
    timeStamp = time.time() - time_interval
    return int(timeStamp)  # Return integer timestamp

def derive_timestamp(timestamp=None,seconds =0,minutes=0, hours=0, days=0, weeks=0,months=0, years=0,*args,**kwargs):
    time_interval = get_time_interval(seconds=seconds,minutes=minutes, hours=hours, days=days, weeks=weeks,months=months, years=years)
    if time_interval:
        timestamp = get_time(time_interval)
    return timestamp
def get_timestamp_from_data(data,*args,**kwargs):
    years = data.get('years',0)
    months = data.get('months',0)
    weeks = data.get('weeks',0)
    days = data.get('days',0)
    hours = data.get('hours',0)
    minutes = data.get('minutes',0)
    seconds = data.get('seconds',0)
    timestamp = data.get('timestamp')
    time_interval = get_time_interval(seconds=seconds,minutes=minutes, hours=hours, days=days, weeks=weeks,months=months, years=years)
    if time_interval:
        timestamp = get_time(time_interval)
    return timestamp

def get_query_result(query, conn):
    """Executes a query and returns the results or commits the transaction."""
    with conn.cursor() as cursor:
        cursor.execute(query)
        if query.strip().lower().startswith("select"):
            return cursor.fetchall()  # Return data for SELECT queries
        conn.commit()

def query_data(query, values=None, error="Error executing query:", zipRows=True):
    """Execute a query and handle transactions with error management."""
    with get_connection() as conn:
        # Choose the cursor type based on whether you want to zip rows with column names
        cursor_factory = DictCursor if zipRows else None
        with conn.cursor(cursor_factory=cursor_factory) as cursor:
            try:
                cursor.execute(query, values)
                result = cursor.fetchall()
                # Log the first row to see its structure
                if result:
                    logging.info("First row data structure: %s", result[0])
                return result
            except Exception as e:
                conn.rollback()
                logging.error("%s %s\nValues: %s\n%s", error, query, values, e)

#####################################
# Fix #1: Correct the usage in fetch_any_combo
#####################################
def fetch_any_combo(columnNames='*',
                    tableName=None,
                    searchColumn=None,
                    searchValue=None,
                    anyValue=False,
                    zipIt=True,
                    schema='public'):
    """
    Fetch rows based on dynamic SQL built from parameters.
    
    :param columnNames: Comma separated columns or '*' for all.
    :param tableName: The table to query. Must not be None or '*'.
    :param searchColumn: The column on which to filter.
    :param searchValue: The value to match in searchColumn.
    :param anyValue: If True, uses = ANY(%s) for arrays.
    :param zipit: If True, uses DictCursor in query_data.
    :param schema: The DB schema.
    """
    if not tableName or tableName == '*':
        logging.error("Invalid tableName provided to fetch_any_combo: %s", tableName)
        return []  # or raise an Exception

    # Build the SELECT list
    if columnNames == '*':
        select_cols = sql.SQL('*')
    else:
        # Convert "col1,col2" -> [col1, col2]
        col_list = [c.strip() for c in columnNames.split(',')]
        select_cols = sql.SQL(", ").join(sql.Identifier(col) for col in col_list)

    # Build the base query: SELECT ... FROM schema.tableName
    base_query = sql.SQL("SELECT {} FROM {}.{}").format(
        select_cols,
        sql.Identifier(schema),
        sql.Identifier(tableName)
    )

    # Build the WHERE clause if needed
    params = []
    if searchColumn and searchValue is not None:
        if anyValue:
            base_query += sql.SQL(" WHERE {} = ANY(%s)").format(sql.Identifier(searchColumn))
            params.append(searchValue if isinstance(searchValue, list) else [searchValue])
        else:
            base_query += sql.SQL(" WHERE {} = %s").format(sql.Identifier(searchColumn))
            params.append(searchValue)

    
    if zipIt:
        result = query_data_as_dict(base_query, values=params)
    else:
        result = query_data(base_query, values=params, zipRows=zipit)
    return result
def get_anything(*args, **kwargs):
    if args:
        for arg in args:
            if 'tableName' not in kwargs:
                kwargs['tableName'] = arg
    response = fetch_any_combo(**kwargs)
    logging.info("Received data: %s", response)  # Log to see the data
    if isinstance(response, list) and len(response) == 1:
        response = response[0]
    return response

def get_table_name_from_query(query):
    """Extract table name from SQL query."""
    if isinstance(query, sql.Composed):
        query = query.as_string(get_connection())  # Convert to string
    parts = query.split()
    if 'from' in parts:
        return parts[parts.index('from') + 1]
    return None

def get_all_pair_info(**kwargs):
    pair = get_pair(**kwargs)
    if not pair:
        return {}
    pair = pair[0]
    pair['meta_data'] = get_meta_data_from_meta_id(pair.get('meta_id'))
    pair['txns'] = get_all_txns_for_pair_id(pair.get('id'))
    return pair

class columnNamesManager(metaclass=SingletonMeta):
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.columnNames = {}

    def get_column_names(self, tableName, schema='public'):
        if tableName not in self.columnNames:
            self.columnNames[tableName] = self.fetch_column_names(tableName, schema)
        return self.columnNames[tableName]

    def fetch_column_names(self, tableName, schema='public'):
        query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = %s
            ORDER BY ordinal_position;
        """
        results = query_data(query, [tableName, schema], error='Error fetching column names')
        if not results:
            logging.warning(f"No columns found for table {tableName} in schema {schema}")
            return []
        return [row[0] for row in results]

    def zip_rows(self, tableName, rows, schema='public'):
        column_names = self.get_column_names(tableName, schema)
        return [dict(zip(column_names, make_list(row))) for row in rows]

def get_pair_id(*args, **kwargs):
    """
    Example function that tries to retrieve a pair's ID by various criteria.
    There's a potential bug with 'is_mint(obj)' references, so watch out for that.
    """
    id_val = None
    for key,value in kwargs.items():
        if key == 'pair_id':
            id_val = value
        if key == 'pair' and isinstance(value, dict):
            id_val = value.get('id')
        if key == 'mint':
            rows = fetch_any_combo(tableName='transactions', searchColumn='mint', searchValue=value)
            if rows:
                id_val = rows[0].get('id')
        if key == 'signature':
            rows = fetch_any_combo(tableName='transactions', searchColumn='signature', searchValue=value)
            if rows:
                id_val = rows[0].get('id')

    for arg in args:
        if is_number(arg):
            id_val = arg
        elif isinstance(arg, dict):
            id_val = arg.get('id')
        # Potential bug fix #2: changed 'obj' -> 'arg'
        # elif is_signature(arg):
        #     ...
        # elif is_mint(arg):
        #     ...
        # etc.

    if id_val:
        return id_val
def get_max_for_row(tableName):
    return query_data(f"SELECT COUNT(*) FROM {tableName};")
#####################################
# Fix #2: Correctly use get_pair_from_* in get_pair
#####################################
def get_pair(mint=None, signature=None, pair_id=None):
    """Retrieve row(s) from 'pairs' table by mint, signature, or pair_id."""
    if pair_id:
        return get_pair_from_pair_id(pair_id)
    elif mint:
        return get_pair_from_mint(mint)
    elif signature:
        return get_pair_from_signature(signature)
    return []

def get_pair_from_mint(mint):
    response = fetch_any_combo(tableName='pairs', searchColumn="mint", searchValue=mint, zipit=True)
    return getZipRows('pairs', response)

def get_pair_from_signature(signature):
    response = fetch_any_combo(tableName='pairs', searchColumn="signature", searchValue=signature, zipit=True)
    return getZipRows('pairs', response)

def get_pair_from_pair_id(pair_id):
    response = fetch_any_combo(tableName='pairs', searchColumn="id", searchValue=pair_id, zipit=True)
    return getZipRows('pairs', response)

def getZipRows(tableName, rows, schema='public'):
    column_names = get_column_names(tableName, schema)
    return [dict(zip(column_names, row)) for row in make_list(rows) if row]

def get_column_names(tableName, schema='public'):
    return columnNamesManager().get_column_names(tableName, schema)

def get_transaction_from_txn_id(txn_id):
    response = fetch_any_combo(tableName='transactions', searchColumn="id", searchValue=txn_id, zipit=True)
    return getZipRows('transactions', response)
def get_transaction_from_signature(signature):
    response = fetch_any_combo(tableName='transactions', searchColumn="signature", searchValue=signature, zipit=True)
    return getZipRows('transactions', response)

def get_transaction_from_log_id(log_id):
    """
    Example that first fetches signature from logdata, then fetches transactions by signature.
    """
    signature_rows = fetch_any_combo(columnNames='signature',
                                     tableName='logdata',
                                     searchColumn='id',
                                     searchValue=log_id,
                                     zipit=True)
    if signature_rows and len(signature_rows) == 1:
        signature = signature_rows[0].get('signature')
        tx_rows = fetch_any_combo(tableName='transactions',
                                  searchColumn='signature',
                                  searchValue=signature,
                                  zipit=True)
        return getZipRows('transactions', tx_rows)
    return []

def get_all_txns_for_pair_id(pair_id):
    response = fetch_any_combo(tableName='transactions', searchColumn='pair_id', searchValue=pair_id, zipit=True)
    return getZipRows('transactions', response)

#####################################
# Fix #3: Add missing signature clause in get_transactions
#####################################
def get_transactions(txn_id=None, log_id=None, signature=None, pair_id=None):
    if pair_id:
        return get_all_txns_for_pair_id(pair_id)
    if txn_id:
        return get_transaction_from_txn_id(txn_id)
    if log_id:
        return get_transaction_from_log_id(log_id)
    if signature:
        return get_transaction_from_signature(signature)
    return []

def get_meta_data_from_mint(mint):
    response = fetch_any_combo(tableName='metadata', searchColumn='mint', searchValue=mint, zipit=True)
    return getZipRows('metadata', response)

def get_meta_data_from_meta_id(meta_id):
    response = fetch_any_combo(tableName='metadata', searchColumn='id', searchValue=meta_id, zipit=True)
    return getZipRows('metadata', response)

def get_meta_data_from_pair_id(pair_id):
    pair_rows = get_pair_from_pair_id(pair_id)
    if not pair_rows:
        return []
    pair = pair_rows[0]
    meta_id = pair.get('meta_id')
    if not meta_id:
        return []
    return get_meta_data_from_meta_id(meta_id)

#####################################
# Fix #4: get_meta_data uses correct references
#####################################
def get_meta_data(pair_id=None, meta_id=None, mint=None):
    if mint:
        return get_meta_data_from_mint(mint)
    if pair_id:
        return get_meta_data_from_pair_id(pair_id)
    if meta_id:
        return get_meta_data_from_meta_id(meta_id)
    return []

#####################################
# Fix #5: Ensure get_all_pair_data aligns with the fixed get_pair
#####################################
def get_all_pair_data(mint=None, signature=None, pair_id=None):
    """
    Gathers pair info, associated transactions, and metadata.
    """
    pair_rows = get_pair(mint=mint, signature=signature, pair_id=pair_id)
    if not pair_rows:
        return {}
    pair = pair_rows[0]
    pair_id_val = pair.get('id')
    mint_val = pair.get('mint')

    pair_data = {}
    pair_data["pair"] = pair
    pair_data["txns"] = get_transactions(pair_id=pair_id_val)
    pair_data["metadata"] = get_meta_data(mint=mint_val)
    return pair_data

def fetch_filtered_transactions_paginated(
    sol_amount, 
    operator=">",
    timestamp_operator=None, 
    limit=50, 
    offset=0,
    years=0,
    months=0,
    weeks=0,
    days=0,
    hours=0,
    minutes=0,
    seconds=0,
    timestamp=None,
    *args,
    **kwargs
):
    # Build the base SQL query.
    # Note that we're filtering on the first element of the JSON array in t.tcns
    query = f"""
        SELECT
            p.*, 
            t.*,
            m.*,
            t2.id AS related_txn
        FROM 
            transactions t
        JOIN 
            pairs p ON t.pair_id = p.id
        LEFT JOIN 
            metadata m ON p.meta_id = m.id
        LEFT JOIN 
            transactions t2 ON t.pair_id = t2.pair_id AND t.signature != t2.signature
        WHERE 
            t.signature IN (
                SELECT signature FROM pairs WHERE signature IS NOT NULL
            )
        AND 
            t.program_id = p.program_id
        AND 
            EXISTS (
                SELECT 1
                FROM jsonb_array_elements(t.tcns) AS elem
                WHERE (elem ->> 'sol_amount')::numeric {operator} %s
    """
    params = [sol_amount]

    # Derive a timestamp cutoff if provided (assuming derive_timestamp is implemented)
    ts = derive_timestamp(
            years=years,
            months=months,
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            timestamp=timestamp)
    
    if ts and timestamp_operator:
        query += f" AND (elem ->> 'timestamp')::bigint {timestamp_operator} %s"
        params.append(int(ts))
    
    # Close the EXISTS clause and add ordering/pagination
    query += ") ORDER BY t.updated_at DESC LIMIT %s OFFSET %s;"
    params.extend([limit, offset])

    return query_data(query, params)
