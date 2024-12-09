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

    // Render the user's message
    renderMessage(`You: ${message}`, "user-message");

    const assistantDiv = document.createElement("div");
    assistantDiv.className = "assistant-message";
    chatDisplay.appendChild(assistantDiv);

    let assistantMessage = "";

    // Handle incoming streamed data
    eventSource.onmessage = (event) => {
        if (event.data === "[END]") {
            eventSource.close(); // Gracefully close the connection
            return;
        }
        assistantMessage += event.data; // Append new chunks to the response
        assistantDiv.textContent = `Assistant: ${assistantMessage.trim()}`; // Update assistant div
    };
    
    // Handle errors during the streaming
    eventSource.onerror = () => {
        console.error("Connection lost while streaming response.");
        assistantDiv.textContent = "Error: Unable to connect to the server.";
        eventSource.close();
    };   

    input.value = ""; // Clear input
};


// Utility Functions
const renderMessage = (message, type) => {
    const div = document.createElement("div");
    div.className = type; // Add appropriate CSS class based on type
    div.textContent = message;
    chatDisplay.appendChild(div);

    // Auto-scroll to the latest message
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
};

// Handle Send Message
const handleSendMessage = () => {
    const message = input.value.trim(); // Clean up user input
    if (!message) {
        alert("Please type a message before sending."); // Notify user
        return;
    }
    streamResponse(message); // Send the message to the backend
    input.value = ""; // Clear the input field
};

