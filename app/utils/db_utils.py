import os
import json
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

# Connect to the database
def connect_db():
    """
    Establish a connection to the database.
    """
    try:
        conn = psycopg.connect(**DB_PARAMS)
        return conn
    except psycopg.OperationalError as e:
        print(f"Database connection error: {e}")
        raise

# Fetch conversations from the database
def fetch_conversations(limit=10):
    """
    Fetch recent conversations from the database.
    """
    conn = connect_db()
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute('SELECT * FROM conversations ORDER BY timestamp DESC LIMIT %s', (limit,))
        conversations = cursor.fetchall()
    conn.close()
    return conversations[::-1]  # Reverse for chronological order

# Store conversations in the database
def store_conversations(prompt, response, metadata):
    """
    Store a conversation in the database.
    """
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(
            '''
            INSERT INTO conversations (timestamp, prompt, response, metadata) 
            VALUES (CURRENT_TIMESTAMP, %s, %s, %s)
            ''',
            (prompt, response, json.dumps(metadata))
        )
    conn.commit()
    conn.close()