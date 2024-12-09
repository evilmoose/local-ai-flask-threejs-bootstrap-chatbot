from flask import Blueprint, render_template, request, jsonify, current_app
import ollama

app = Blueprint('app', __name__)

convo = []

def stream_response(prompt):
    convo.append({'role': 'user', 'content': prompt})  # Add user's message to convo
    response = ''
    try:
        stream = ollama.chat(model='llama3.2', messages=convo, stream=True)
        for chunk in stream:
            content = chunk.get('message', {}).get('content', '')
            response += content
            yield content
    except Exception as e:
        print(f"Error in stream_response: {e}")
        yield f"data: Error occurred while generating response\n\n"


    convo.append({'role': 'assistant', 'content': response})  # Add assistant's response to convo

@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        prompt = request.args.get("message", "")
        print(f"Received GET request with prompt: {prompt}")  # Debug log

        if not prompt.strip():
            return jsonify({"error": "Please type a message before sending."}), 400

        def generate_response():
            for chunk in stream_response(prompt):
                print(f"Streaming chunk: {chunk}")  # Debug log
                yield f"data: {chunk}\n\n"
            yield "data: [END]\n\n"

        return current_app.response_class(generate_response(), content_type="text/event-stream")



