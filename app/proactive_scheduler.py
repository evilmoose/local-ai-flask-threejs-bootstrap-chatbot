from apscheduler.schedulers.background import BackgroundScheduler
from .utils.context_manager import get_user_context
from .utils.db_utils import connect_db
from datetime import datetime

scheduler = BackgroundScheduler()
# In the future interval will be determine by some algorythm that looks at chat history and see how often messages come in and some other variables.
# import os
# interval_seconds = int(os.getenv("PROACTIVE_MESSAGE_INTERVAL", 10))  # Default to 10 seconds
def send_proactive_message():
    start_time = datetime.now()
    print(f"DEBUG: Proactive message job started at {start_time}")
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT user_id, last_topic
                    FROM user_context
                    WHERE last_message_time < NOW() - INTERVAL '2 minutes'
                """)
                inactive_users = cursor.fetchall()
                print(f"DEBUG: Inactive users: {inactive_users}")

        for user_id, last_topic in inactive_users:
            message = f"Hi! It's been a while since we last chatted about {last_topic or 'something interesting'}. What's on your mind?"
            print(f"DEBUG: Sending proactive message for User {user_id}: {message}")

            # Update last_message_time to avoid re-selecting the same user
            with connect_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE user_context
                        SET last_message_time = NOW()
                        WHERE user_id = %s
                    """, (user_id,))
                conn.commit()

    except Exception as e:
        print(f"ERROR: Exception in proactive message job: {e}")
    finally:
        end_time = datetime.now()
        print(f"DEBUG: Proactive message job ended at {end_time}")

def schedule_proactive_messages():
    if scheduler.get_job("proactive_message_job"):
        print("Removing stale proactive message job.")
        scheduler.remove_job("proactive_message_job")

    # Schedule the proactive message job
    scheduler.add_job(
        send_proactive_message,
        "interval",
        seconds=120,
        id="proactive_message_job"
    )
    print("DEBUG: Proactive message job scheduled.")

    # Start the scheduler if not already running
    
    scheduler.start()





