from apscheduler.schedulers.background import BackgroundScheduler
from .utils.context_manager import get_user_context

scheduler = BackgroundScheduler()

def send_proactive_message(user_id):
    context = get_user_context(user_id)
    message = f"Hi! Last time, we discussed {context.get('last_topic', 'interesting topics')}."
    print(f"Proactive Message to User {user_id}: {message}")

def schedule_proactive_messages():
    scheduler.add_job(send_proactive_message, "interval", hours=6, args=[1])
    scheduler.start()
