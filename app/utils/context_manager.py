import psycopg
import json
from psycopg.rows import dict_row
from .db_utils import connect_db

def get_user_context(user_id):
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT last_topic, mood, interaction_count, last_interaction_type, additional_data
            FROM user_context
            WHERE user_id = %s
        """, (user_id,))
        result = cursor.fetchone()
    conn.close()

    if not result:
        print(f"DEBUG: No context found for user_id={user_id}, returning defaults.")
        return {
            "last_topic": None,
            "mood": "neutral",
            "interaction_count": 0,
            "last_interaction_type": "chat",
            "additional_data": {}
        }

    return {
        "last_topic": result[0],
        "mood": result[1],
        "interaction_count": result[2],
        "last_interaction_type": result[3],
        "additional_data": result[4]
    }


def update_user_context(user_id, context_update):
    """
    Update the context for a given user ID.
    """
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE user_context
            SET 
                last_topic = COALESCE(%s, last_topic),
                mood = COALESCE(%s, mood),
                interaction_count = interaction_count + 1,
                last_interaction_type = COALESCE(%s, last_interaction_type),
                additional_data = additional_data || %s::jsonb,
                last_active = NOW()
            WHERE user_id = %s
        """, (
            context_update.get("last_topic"),
            context_update.get("mood", None),
            context_update.get("last_interaction_type", None),
            json.dumps(context_update.get("additional_data", {})),
            user_id
        ))
    conn.commit()
    conn.close()