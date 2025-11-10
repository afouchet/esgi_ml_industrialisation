import re
from typing import Optional

def create_undo_query(sql_query: str) -> str:
    """
    Generate an undo SQL query for a given SQL statement.
    
    Limitations:
    - UPDATE/DELETE: Cannot restore original data without knowing it beforehand
    - TRUNCATE/DROP: Cannot be undone without backups
    - Complex queries: May not handle all edge cases
    
    Args:
        sql_query: The SQL query to generate an undo for
        
    Returns:
        The undo SQL query as a string
        
    Raises:
        ValueError: If the query type is not supported or cannot be undone
    """
    # Normalize the query
    query = sql_query.strip().rstrip(';')
    query_upper = query.upper()
    
    # Determine query type
    if query_upper.startswith('INSERT'):
        return _undo_insert(query)
    elif query_upper.startswith('UPDATE'):
        return _undo_update(query)
    elif query_upper.startswith('DELETE'):
        return _undo_delete(query)
    elif query_upper.startswith('CREATE TABLE'):
        return _undo_create_table(query)
    elif query_upper.startswith('DROP TABLE'):
        return _undo_drop_table(query)
    elif query_upper.startswith('ALTER TABLE'):
        return _undo_alter_table(query)
    else:
        raise ValueError(f"Unsupported query type or cannot generate undo for: {query[:50]}...")


def _undo_insert(query: str) -> str:
    """Generate undo for INSERT statement."""
    # Pattern: INSERT INTO table_name ...
    match = re.search(r'INSERT\s+INTO\s+([^\s(]+)', query, re.IGNORECASE)
    if not match:
        raise ValueError("Could not parse table name from INSERT query")
    
    table_name = match.group(1)
    
    # Try to extract values for WHERE clause
    # Handle INSERT INTO table (col1, col2) VALUES (val1, val2)
    values_match = re.search(r'VALUES\s*\((.*?)\)', query, re.IGNORECASE | re.DOTALL)
    cols_match = re.search(r'\(([^)]+)\)\s*VALUES', query, re.IGNORECASE)
    
    if values_match and cols_match:
        columns = [col.strip() for col in cols_match.group(1).split(',')]
        values = [val.strip() for val in values_match.group(1).split(',')]
        
        where_conditions = ' AND '.join([f"{col} = {val}" for col, val in zip(columns, values)])
        return f"DELETE FROM {table_name} WHERE {where_conditions}"
    else:
        # Fallback: delete last inserted row (requires primary key or unique constraint)
        raise ValueError("Cannot create specific DELETE without column/value information. "
                       "Consider using DELETE with appropriate WHERE clause manually.")


def _undo_update(query: str) -> str:
    """Generate undo for UPDATE statement - requires original data."""
    raise ValueError("UPDATE cannot be undone without knowing the original data. "
                   "You must store the original values before executing UPDATE. "
                   "Consider using: SELECT * FROM table WHERE <condition> before UPDATE.")


def _undo_delete(query: str) -> str:
    """Generate undo for DELETE statement - requires original data."""
    raise ValueError("DELETE cannot be undone without knowing the deleted data. "
                   "You must store the deleted rows before executing DELETE. "
                   "Consider using: SELECT * FROM table WHERE <condition> before DELETE.")


def _undo_create_table(query: str) -> str:
    """Generate undo for CREATE TABLE statement."""
    match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\s(]+)', query, re.IGNORECASE)
    if not match:
        raise ValueError("Could not parse table name from CREATE TABLE query")
    
    table_name = match.group(1)
    return f"DROP TABLE IF EXISTS {table_name}"


def _undo_drop_table(query: str) -> str:
    """Generate undo for DROP TABLE statement."""
    raise ValueError("DROP TABLE cannot be undone without a backup or schema definition. "
                   "You must have the CREATE TABLE statement stored beforehand.")


def _undo_alter_table(query: str) -> str:
    """Generate undo for ALTER TABLE statement."""
    query_upper = query.upper()
    
    # ADD COLUMN
    if 'ADD COLUMN' in query_upper or 'ADD ' in query_upper:
        match = re.search(r'ALTER\s+TABLE\s+([^\s]+)\s+ADD\s+(?:COLUMN\s+)?([^\s]+)', query, re.IGNORECASE)
        if match:
            table_name = match.group(1)
            column_name = match.group(2)
            return f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
    
    # DROP COLUMN
    if 'DROP COLUMN' in query_upper or 'DROP ' in query_upper:
        raise ValueError("ALTER TABLE DROP COLUMN cannot be undone without knowing the column definition.")
    
    # RENAME
    if 'RENAME' in query_upper:
        # RENAME TABLE old TO new -> RENAME TABLE new TO old
        match = re.search(r'RENAME\s+TABLE\s+([^\s]+)\s+TO\s+([^\s]+)', query, re.IGNORECASE)
        if match:
            old_name = match.group(1)
            new_name = match.group(2)
            return f"RENAME TABLE {new_name} TO {old_name}"
        
        # RENAME COLUMN old TO new
        match = re.search(r'ALTER\s+TABLE\s+([^\s]+)\s+RENAME\s+COLUMN\s+([^\s]+)\s+TO\s+([^\s]+)', 
                         query, re.IGNORECASE)
        if match:
            table_name = match.group(1)
            old_col = match.group(2)
            new_col = match.group(3)
            return f"ALTER TABLE {table_name} RENAME COLUMN {new_col} TO {old_col}"
    
    raise ValueError(f"Cannot generate undo for this ALTER TABLE query: {query[:50]}...")


# Example usage
if __name__ == "__main__":
    test_queries = [
        "INSERT INTO purchases (user_id, drug_id, quantity, unit_price, total_amount, purchase_date) VALUES (2, 2, 10, 0.01, 0.1, '2025-07-01');",
    ]
    
    for query in test_queries:
        print(f"Original: {query}")
        try:
            undo = create_undo_query(query)
            print(f"Undo:     {undo}")
        except ValueError as e:
            print(f"Error:    {e}")
        print()
