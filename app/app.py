import os
from dotenv import load_dotenv
from flask import Blueprint, render_template, request, jsonify, current_app
import psycopg
from psycopg.rows import dict_row
import ollama
import json

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

app = Blueprint('app', __name__)

# Connect to the database
def connect_db():
    try:
        conn = psycopg.connect(**DB_PARAMS)
        return conn
    except psycopg.OperationalError as e:
        print(f"Database connection error: {e}")
        raise

# Fetch conversations from the database
def fetch_conversations(limit=10):
    conn = connect_db()
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute('SELECT * FROM conversations ORDER BY timestamp DESC LIMIT %s', (limit,))
        conversations = cursor.fetchall()
    conn.close()
    return conversations[::-1]  # Reverse for chronological order

# Store conversations in the database
def store_conversations(prompt, response, metadata):
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

# Load the dataset
def load_dataset(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Load Rebecca's dataset and preprocess for lookups
rebecca_dataset = load_dataset("rebecca_dataset.json")
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
def query_local_model_with_dataset(prompt):
    entry = dataset_lookup.get(prompt.lower())

    if entry:
        dataset_response = entry["output"]
        metadata = entry.get("metadata", {})
    else:
        dataset_response = None
        metadata = get_default_metadata()

    messages = construct_messages(prompt, dataset_response)
    response = query_llm(messages)
    return {"response": response, "metadata": metadata}

# Generate and stream chatbot responses
def stream_response(prompt):
    try:
        result = query_local_model_with_dataset(prompt)
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
            for chunk in stream_response(prompt):
                yield f"data: {chunk}\n\n"

        return current_app.response_class(
            generate_response(),
            content_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )

@app.route("/reset", methods=["POST"])
def reset():
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute('TRUNCATE TABLE conversations RESTART IDENTITY')
    conn.commit()
    conn.close()
    return jsonify({"message": "Conversation history reset."})
