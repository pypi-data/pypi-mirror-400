from abstract_utilities import make_list,SingletonMeta
from .queries import query_data
from psycopg2 import sql, connect
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
        results = query_data(query, [tableName, schema], error='Error fetching column names',zipRows=False)
        if results:
            return [row[0] for row in results]
        logging.warning(f"No columns found for table {tableName} in schema {schema}")
    def zip_rows(self, tableName, rows, schema='public'):
        column_names = self.get_column_names(tableName, schema)
        if rows:
            return [dict(zip(columnNames,make_list(row))) for row in rows]
#####################################
# Fix #1: Correct the usage in fetch_any_combo
#####################################
from psycopg2 import sql
import logging

def fetch_any_combo(columnNames='*',
                    tableName=None,
                    searchColumn=None,
                    searchValue=None,
                    count=False,
                    anyValue=False,
                    zipit=True,
                    schema='public'):
    """
    Fetch rows based on dynamic SQL built from parameters.

    :param columnNames: Comma separated columns or '*' for all.
    :param tableName: The table to query. Must not be None or '*'.
    :param searchColumn: The column on which to filter.
    :param searchValue: The value to match in searchColumn.
    :param anyValue: If True, uses = ANY(%s) for arrays.
    :param count: If True, returns a count of the matching rows.
    :param zipit: If True, uses DictCursor in query_data.
    :param schema: The DB schema.
    """
    if not tableName or tableName == '*':
        logging.error("Invalid tableName provided to fetch_any_combo: %s", tableName)
        return []  # or raise an Exception

    # Build the SELECT list
    if count:
        # If counting and either all columns (*) or more than one column is provided,
        # use COUNT(*) since COUNT(col1, col2) is not valid SQL.
        if columnNames == '*' or ',' in columnNames:
            select_cols = sql.SQL("COUNT(*)")
        else:
            # Only one column is provided, so count that column.
            select_cols = sql.SQL("COUNT({})").format(sql.Identifier(columnNames.strip()))
    else:
        if columnNames == '*':
            select_cols = sql.SQL('*')
        else:
            # Split comma-separated columns and create a SQL fragment.
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
            # Use col = ANY(%s) which expects searchValue to be a list/array.
            base_query += sql.SQL(" WHERE {} = ANY(%s)").format(sql.Identifier(searchColumn))
            params.append(make_list(searchValue))
        else:
            base_query += sql.SQL(" WHERE {} = %s").format(sql.Identifier(searchColumn))
            params.append(searchValue)
    
    return query_data(base_query, values=params, zipRows=zipit)

def get_column_names(tableName,schema='public'):
    return columnNamesManager().get_column_names(tableName,schema)
def getZipRows(tableName, rows, schema='public'):
    columnNames = get_column_names(tableName,schema)
    if columnNames:
        return [dict(zip(columnNames,row)) for row in make_list(rows) if row]
def get_db_from(tableName=None,columnNames=None,searchColumn=None,searchValue=None,count=False,zipit=True):
    columnNames=columnNames or '*'
    if isinstance(columnNames,list):
        columnNames = ','.join(columnNames)
    response = fetch_any_combo(tableName=tableName,columnNames=columnNames,searchColumn=searchColumn,searchValue=searchValue,zipit=zipit,count=count)
    return response
