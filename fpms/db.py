import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """
    Establishes a connection to the MySQL database.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='finance'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def execute_query(query, params=None, fetch=False, fetchall=True):
    """
    Executes a SQL query.
    - query: The SQL string (use %s for parameters).
    - params: Tuple of parameters to avoid SQL injection.
    - fetch: True if SELECT query, False for INSERT/UPDATE/DELETE.
    - fetchall: True to return all rows, False to return a single row.
    """
    connection = get_db_connection()
    if not connection:
        return None

    try:
        # Use dictionary cursor to return rows as dictionaries
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            if fetchall:
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()
            return result
        else:
            connection.commit()
            return cursor.lastrowid
            
    except Error as e:
        print(f"Error executing query: {e}")
        if connection:
            connection.rollback()
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
