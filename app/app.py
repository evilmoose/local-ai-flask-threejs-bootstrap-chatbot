from flask import Blueprint, render_template, request, jsonify, current_app
from .proactive_scheduler import schedule_proactive_messages
from .chat_settings import get_chat_settings, update_chat_settings
from .utils.context_manager import get_user_context, update_user_context
from datetime import datetime
from .utils.db_utils import connect_db
import ollama
import json
import time

app = Blueprint('app', __name__)

# Start proactive message scheduling
schedule_proactive_messages()

# Load the dataset
def load_dataset(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Load Rebecca's dataset and preprocess for lookups
rebecca_dataset = load_dataset("./app/rebecca_dataset.json")
dataset_lookup = {entry["input"].lower(): entry for entry in rebecca_dataset}

# Default metadata as a reusable constant
DEFAULT_METADATA = {
    "topic": "general",
    "mood": "neutral",
    "feedback": []
}

# Helper function for default metadata
def get_default_metadata():
    return DEFAULT_METADATA.copy()

# Helper function to construct messages
def construct_messages(prompt, dataset_response=None, user_context=None):
    # Step 1: Create a warm system message
    system_message = "You are a friendly and witty conversational assistant."

    # Step 2: Add user-specific context
    if user_context and "last_topic" in user_context:
        context_summary = f"Previously, you discussed: {user_context['last_topic']}."
        system_message += f" {context_summary}"

    # Step 3: Prepare the message array
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    # Step 4: Include dataset response if available
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
def process_message(prompt, user_id):
    print(f"DEBUG: Starting query_local_model_with_dataset with prompt='{prompt}' and user_id={user_id}")
    
    # Step 1: Fetch user context
    user_context = get_user_context(user_id)
    print(f"DEBUG: user_context={user_context}")
    if user_context is None:
        user_context = {}

    last_topic = user_context.get("last_topic", None)
    print(f"DEBUG: last_topic={last_topic}")

    # Step 2: Enhance dataset lookup with context
    entry = dataset_lookup.get(f"{last_topic}:{prompt.lower()}") or dataset_lookup.get(prompt.lower())
    print(f"DEBUG: dataset_lookup entry={entry}")

    if entry:
        dataset_response = entry.get("output")
        metadata = entry.get("metadata", {})
    else:
        dataset_response = None
        metadata = get_default_metadata()

    # Ensure metadata contains user context
    metadata["user_context"] = user_context
    print(f"DEBUG: metadata={metadata}")

    # Step 4: Construct messages with context
    messages = construct_messages(prompt, dataset_response, user_context)
    print(f"DEBUG: messages={messages}")

    # Step 5: Query the LLM for a response
    response = query_llm(messages)
    print(f"DEBUG: response={response}")

    # Step 6: Update user context dynamically
    update_user_context(user_id, {"last_topic": prompt})

    return {"response": response, "metadata": metadata}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        prompt = request.args.get("message", "").strip()
        user_id = request.args.get("user_id", 1)
        if not prompt:
            return jsonify({"error": "Please type a message before sending."}), 400

        def generate_response():
            try:
                # Generate response using LLM
                result = process_message(prompt, user_id)
                response = result["response"]

                # Simulate chunked responses
                for chunk in response.split("\n"):  # Example: Split by newline
                    yield f"data: {chunk}\n\n"  # SSE format
                    time.sleep(0.5)  # Simulate delay for processing each chunk

                yield "[END]\n\n"  # Signal completion
            except Exception as e:
                print(f"Error in generate_response: {e}")
                yield "data: Error occurred while generating response\n\n"

        return current_app.response_class(
            generate_response(),
            content_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    elif request.method == "POST":
        # Non-streaming POST for simpler use cases
        data = request.json
        user_id = data.get("user_id")
        user_message = data.get("message")

        response = process_message(user_message, user_id)
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE user_context
                    SET last_message_time = NOW()
                    WHERE user_id = %s
                """, (user_id,))
            conn.commit()

        return jsonify({"response": response})


@app.route("/proactive", methods=["GET"])
def proactive():
    def generate_proactive_message():
        try:
            while True:
                yield f"data: Proactive message at {datetime.now()}\n\n"
                time.sleep(5)
        except GeneratorExit:
            print("DEBUG: Client disconnected from EventSource.")
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            print("DEBUG: Closing EventSource connection.")

    return current_app.response_class(
        generate_proactive_message(),
        content_type="text/event-stream"
    )

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "GET":
        return jsonify(get_chat_settings())
    elif request.method == "POST":
        data = request.json
        updated_settings = update_chat_settings(data)
        return jsonify(updated_settings)

@app.route("/reset", methods=["POST"])
def reset():
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute('TRUNCATE TABLE conversations RESTART IDENTITY')
    conn.commit()
    conn.close()
    return jsonify({"message": "Conversation history reset."})

