# Rebecca: Local AI Chatbot with Proactive Features

## Overview
Rebecca is a warm, engaging, and proactive chatbot application designed for personalized and meaningful interactions. Built using Flask and Llama3.2, Rebecca employs advanced contextual awareness, proactive messaging, and a friendly tone to create an emotionally intelligent companion/assistant/chatbot.

---

## Key Features
1. **Proactive Messaging**: 
   - Initiates conversations using personalized greetings and contextual follow-ups.
   - Time-based triggers to engage inactive users.

2. **Contextual Awareness**:
   - Tracks user interactions and maintains conversation context for meaningful replies.
   - Stores metadata such as mood, topics, and preferences.

3. **Custom Personality**:
   - Rebecca's responses are warm, empathetic, and creative, tailored to user needs using `rebecca_dataset.json`.

4. **Database-Driven**:
   - PostgreSQL integration for storing conversations and user-specific context.

5. **Real-Time Interaction**:
   - Streams responses dynamically for a seamless user experience.

---

## Project Structure

```
project/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css          # Frontend styles
│   │   ├── js/
│   │   │   └── app.js              # Frontend logic
│   ├── templates/
│   │   └── index.html              # Chat interface
│   ├── utils/
│   │   ├── context_manager.py      # Manages user context operations
│   │   ├── db_utils.py             # Database utilities
│   │   └── __init__.py             # Utility module initializer
│   ├── app.py                      # Main Flask app
│   ├── chat_settings.py            # Chatbot configurations
│   ├── proactive_scheduler.py      # Schedules proactive messages
│   └── rebecca_dataset.json        # Predefined dataset for responses
├── .env                            # Environment variables
├── requirements.txt                # Python dependencies
├── run.py                          # Entry point for the app
├── README.md                       # Documentation
```

---

## Installation and Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Node.js (optional for frontend enhancements)

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo.git
   cd your-repo
   ```

2. **Set up the Python Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate     # For Windows
   pip install -r requirements.txt
   ```

3. **Configure `.env`**:
   Create a `.env` file with:
   ```
   DATABASE_URL=postgresql://user:password@localhost/memory_agent
   SECRET_KEY=your-secret-key
   ```

4. **Set up the PostgreSQL Database**:
   - Create the database `memory_agent`.
   - Run the following commands to set up the schema:
     ```sql
     CREATE TABLE conversations (
         id SERIAL PRIMARY KEY,
         timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         prompt TEXT NOT NULL,
         response TEXT NOT NULL,
         metadata JSONB DEFAULT '{}'
     );

     CREATE TABLE user_context (
         user_id SERIAL PRIMARY KEY,
         context JSONB DEFAULT '{}',
         last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
     );
     ```

5. **Run the Flask App**:
   ```bash
   python run.py
   ```

6. **Access the Chat Interface**:
   Open `http://127.0.0.1:5000` in your browser.

---

## Features in Detail

### **1. Contextual Awareness**
Rebecca tracks user interactions and stores context in the database. This enables Rebecca to:
- Reference past conversations.
- Adapt replies based on user preferences.

### **2. Proactive Messaging**
Rebecca initiates conversations:
- **Examples**:
  - "Good morning! What’s on your mind today?"
  - "Hi! Last time, we talked about your project. How’s it going?"
- Proactive messages are triggered by inactivity or time-based events.

### **3. Personalized Responses**
Rebecca uses `rebecca_dataset.json` to provide tailored replies with metadata-driven insights:
- **Example Dataset Entry**:
  ```json
  {
      "instruction": "Respond warmly and empathetically.",
      "input": "I've been feeling lonely lately.",
      "output": "I'm so glad you reached out. Loneliness can be tough, but you're not alone in this. What's been on your mind?",
      "metadata": {
          "topic": "emotions",
          "mood": "lonely",
          "feedback": []
      }
  }
  ```

---

## API Endpoints

### `/chat`
- **Method**: `GET`
- **Description**: Streams Rebecca's response to a user's input.
- **Parameters**: 
  - `message` (string): The user’s input.

### `/reset`
- **Method**: `POST`
- **Description**: Resets the user context and clears the conversation history.

---

## Frontend Features

### **Dynamic Chat Display**
- Displays user and assistant messages with contextual animations.
- Proactively shows messages without requiring user input.

### **Typing Indicator**
- Simulates Rebecca "thinking" while generating responses.

### **Responsive Design**
- Supports both desktop and mobile views.

---

## Development Notes

### **Testing**
1. **Unit Tests**:
   - Test `query_local_model_with_dataset` with various prompts and user contexts.
   - Validate proactive message triggers.
2. **Integration Tests**:
   - Ensure database interactions work seamlessly with `user_context`.

### **Custom Dataset Training**
- Expand `rebecca_dataset.json` with more scenarios.
- Use Hugging Face's Trainer API for fine-tuning Llama3.2.

---

## Future Enhancements
- **Feedback Mechanism**: Allow users to rate responses to improve Rebecca’s performance.
- **Advanced Context Management**: Implement multi-turn conversation tracking with nested topics.
- **Dynamic Personality Profiles**: Enable Rebecca to adapt her tone based on user preferences.

---

## License
This project is open-source under the MIT License.

---

## Acknowledgments
Special thanks to open-source contributors and frameworks like Flask, PostgreSQL, and Hugging Face for enabling this project.

