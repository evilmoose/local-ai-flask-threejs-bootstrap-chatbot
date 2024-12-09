// Globals
const input = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");
const chatDisplay = document.getElementById("chat-display");

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
    if (!sendButton.listenerAttached) {
        sendButton.addEventListener("click", handleSendMessage);
        sendButton.listenerAttached = true; // Prevent re-attachment
    }
});


// Streaming Chat Logic
const streamResponse = (message) => {
    const eventSource = new EventSource(`/chat?message=${encodeURIComponent(message)}`);

    renderMessage(`You: ${message}`, "user-message");

    const assistantDiv = document.createElement("div");
    assistantDiv.className = "assistant-message";
    chatDisplay.appendChild(assistantDiv);

    let assistantMessage = "";

    eventSource.onmessage = (event) => {
        if (event.data === "[END]") {
            eventSource.close(); // Gracefully close the connection
            return;
        }
        assistantMessage += event.data; // Append new chunks to the response
        assistantDiv.textContent = assistantMessage.trim(); // Update assistant div
    };
    
    eventSource.onerror = () => {
        console.error("Connection lost while streaming response.");
        renderMessage("Error: Unable to connect to the server.", "error-message");
        eventSource.close();
    };
      

    input.value = ""; // Clear input
};


// Utility Functions
const renderMessage = (message, type) => {
    const div = document.createElement("div");
    div.className = type;
    div.textContent = message;
    chatDisplay.appendChild(div);
    chatDisplay.scrollTop = chatDisplay.scrollHeight; // Auto-scroll to the latest message
};

// Handle Send Message
const handleSendMessage = () => {
    const message = input.value.trim();
    if (!message) {
        alert("Please type a message before sending."); // Notify user
        return;
    }
    streamResponse(message);
    input.value = ""; // Clear input
};

