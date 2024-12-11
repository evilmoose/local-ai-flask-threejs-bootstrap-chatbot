from flask import Blueprint, render_template, request, jsonify, current_app
from apscheduler.schedulers.background import BackgroundScheduler
from .chat_settings import get_chat_settings, update_chat_settings
from .utils.context_manager import get_user_context, update_user_context
from .utils.db_utils import connect_db
import ollama
import json

app = Blueprint('app', __name__)

# Scheduler for proactive messages
scheduler = BackgroundScheduler()
scheduler.start()

# Load the dataset
def load_dataset(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Load Rebecca's dataset and preprocess for lookups
rebecca_dataset = load_dataset("./app/rebecca_dataset.json")
dataset_lookup = {entry["input"].lower(): entry for entry in rebecca_dataset}

# Default metadata as a reusable constant
DEFAULT_METADATA = {"topic": "unknown", "mood": "neutral", "feedback": []}

# Helper function for default metadata
def get_default_metadata():
    return DEFAULT_METADATA.copy()

# Helper function to construct messages
def construct_messages(prompt, dataset_response=None):
    messages = [
        {"role": "system", "content": "You are a friendly and witty conversational assistant."},
        {"role": "user", "content": prompt}
    ]
    if dataset_response:
        messages.append({
            "role": "assistant",
            "content": f"This is a suggested response: {dataset_response}. Please refine it to make it more original while maintaining tone."
        })
    return messages

# Helper function to query the LLM
def query_llm(messages):
    response = ''
    try:
        stream = ollama.chat(model='llama3.2', messages=messages, stream=True)
        for chunk in stream:
            response += chunk.get('message', {}).get('content', '')
    except Exception as e:
        print(f"Error querying local model: {e}")
        response = "Error generating a response."
    return response.strip()

# Main function: Query local model with dataset
def query_local_model_with_dataset(prompt, user_id):
    # Intergrate user context
    user_context = get_user_context(user_id)
    entry = dataset_lookup.get(prompt.lower())

    if entry:
        dataset_response = entry["output"]
        metadata = entry.get("metadata", {})
    else:
        dataset_response = None
        metadata = get_default_metadata()

    messages = construct_messages(prompt, dataset_response)
    response = query_llm(messages)

    # Update user context
    update_user_context(user_id, {"last_topic": prompt})

    return {"response": response, "metadata": metadata}

# Generate and stream chatbot responses
def stream_response(prompt):
    try:
        result = query_local_model_with_dataset(prompt, user_id=1)
        response = result["response"]

        first_chunk = True  # State to track if it's the first chunk

        for chunk in response.split('\n'):
            cleaned_chunk = chunk.strip()
            print(f"Streaming text chunk: {cleaned_chunk}")  # Debugging log

            # Add "Rebecca:" prefix only for the first chunk
            if first_chunk:
                yield f"Rebecca: {cleaned_chunk}\n\n"
                first_chunk = False  # Update state
            else:
                yield f"{cleaned_chunk}\n\n"

        # Send [END] and reset state
        yield "[END]\n\n"

    except Exception as e:
        print(f"Error in stream_response: {e}")
        yield f"data: Error occurred while generating response\n\n"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        prompt = request.args.get("message", "").strip()
        if not prompt:
            return jsonify({"error": "Please type a message before sending."}), 400

        def generate_response():
            try:
                result = query_local_model_with_dataset(prompt, user_id=1)
                response = result["response"]

                for chunk in response.split('\n'):
                    yield f"data: {chunk}\n\n"  # Proper SSE format
                yield "data: [END]\n\n"
            except Exception as e:
                print(f"Error in generate_response: {e}")
                yield "data: Error occurred while generating response\n\n"

        return current_app.response_class(
            generate_response(),
            content_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "GET":
        return jsonify(get_chat_settings())
    elif request.method == "POST":
        data = request.json
        updated_settings = update_chat_settings(data)
        return jsonify(updated_settings)
    
# Proactive message example
def send_proactive_message(user_id):
    user_context = get_user_context(user_id)
    message = f"Hi! Last time, we discussed {user_context.get('last_topic', 'interesting topics')}."
    print(f"Proactive Message to User {user_id}: {message}")

@app.route("/reset", methods=["POST"])
def reset():
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute('TRUNCATE TABLE conversations RESTART IDENTITY')
    conn.commit()
    conn.close()
    return jsonify({"message": "Conversation history reset."})

# Schedule proactive messages
scheduler.add_job(
    send_proactive_message,
    "interval",
    hours=6,
    args=[1]  # Example user ID
)
