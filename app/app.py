from flask import Blueprint, render_template, request, jsonify
import ollama  # Assuming you're using the Ollama library

app = Blueprint('app', __name__)

conversations = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400
    
    # Pass the user message to the chatbot model
    try:
        response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": user_message}])
        assistant_response = response['message']['content']  # Extract content from chatbot response
    except Exception as e:
        assistant_response = f"Error: {str(e)}"

    conversations.append({"user": user_message, "assistant": assistant_response})
    return jsonify({"response": assistant_response, "conversations": conversations})

