import psycopg
import json
from psycopg.rows import dict_row
from .db_utils import connect_db

def get_user_context(user_id):
    """
    Fetch the context for a given user ID.
    """
    conn = connect_db()
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute("SELECT context FROM user_context WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
    conn.close()
    return result["context"] if result else {}

def update_user_context(user_id, context_update):
    """
    Update the context for a given user ID.
    """
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE user_context SET context = context || %s WHERE user_id = %s",
            (json.dumps(context_update), user_id)
        )
    conn.commit()
    conn.close()