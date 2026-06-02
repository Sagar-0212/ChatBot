import sqlite3
import os
import sys

# Ensure parent directory is in path when this module is loaded
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    Configures the connection to enable foreign keys and return dictionary-like sqlite3.Row objects.
    """
    db_path = Config.get_sqlite_db_path()
    
    # Resolve database path relative to project root if it is relative
    if not os.path.isabs(db_path):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(project_root, db_path)
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def query_db(query, args=(), one=False):
    """
    Runs a SELECT query against the database and returns Row objects.
    
    :param query: SQL string to execute.
    :param args: Tuple of parameters to bind.
    :param one: If True, returns only the first record or None.
    :return: A list of sqlite3.Row objects, a single Row, or None.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, args)
        rows = cursor.fetchall()
        return (rows[0] if rows else None) if one else rows
    finally:
        conn.close()

def insert_db(query, args=()):
    """
    Runs an INSERT, UPDATE, or DELETE query and commits the changes.
    
    :param query: SQL string to execute.
    :param args: Tuple of parameters to bind.
    :return: The row id of the last inserted row or None.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
