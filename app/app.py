import os
from dotenv import load_dotenv
from flask import Blueprint, render_template, request, jsonify, current_app
import psycopg
from psycopg.rows import dict_row
import ollama

# Load environment variables from .env file
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

# convo = []

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
def store_conversations(prompt, response):
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(
            '''
            INSERT INTO conversations (timestamp, prompt, response) 
            VALUES (CURRENT_TIMESTAMP, %s, %s)
            ''',
            (prompt, response)
        )
    conn.commit()
    conn.close()

# Generate and stream chatbot responses
def stream_response(prompt):
    # convo.append({'role': 'user', 'content': prompt})  # Add user's message to convo

    # Fetch conversation history for context
    conversation_history = fetch_conversations()

    # Prepare messages for the model
    messages = [
        {'role': 'user', 'content': row['prompt']} if row['response'] is None else
        {'role': 'assistant', 'content': row['response']}
        for row in conversation_history
    ]
    messages.append({'role': 'user', 'content': prompt})  # Add the current prompt

    response = ''
    try:
        stream = ollama.chat(model='llama3.2', messages=messages, stream=True)
        for chunk in stream:
            content = chunk.get('message', {}).get('content', '')
            response += content
            yield content
    except Exception as e:
        print(f"Error in stream_response: {e}")
        yield f"data: Error occurred while generating response\n\n"


    # Update the assistant's response in the database
    store_conversations(prompt, response)

@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")

# chat route
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        prompt = request.args.get("message", "").strip()
        #print(f"Received GET request with prompt: {prompt}")  # Debug log

        if not prompt:
            return jsonify({"error": "Please type a message before sending."}), 400

        def generate_response():
            for chunk in stream_response(prompt):
                #print(f"Streaming chunk: {chunk}")  # Debug log
                yield f"data: {chunk}\n\n"
            yield "data: [END]\n\n"

        return current_app.response_class(generate_response(), content_type="text/event-stream")
    
# Reset conversation history
@app.route("/reset", methods=["POST"])
def reset():
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute('TRUNCATE TABLE conversations RESTART IDENTITY')
    conn.commit()
    conn.close()
    return jsonify({"message": "Conversation history reset."})





