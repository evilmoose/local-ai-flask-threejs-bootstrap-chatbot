const input = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");
const chatDisplay = document.getElementById("chat-display");
const typingIndicator = document.getElementById("typing-indicator");
const darkModeToggle = document.getElementById("dark-mode-toggle");

document.addEventListener("DOMContentLoaded", () => {
    if (!sendButton.listenerAttached) {
        sendButton.addEventListener("click", handleSendMessage);
        sendButton.listenerAttached = true;
    }

    darkModeToggle.addEventListener("click", toggleDarkMode);
});

const streamResponse = (message) => {
    const eventSource = new EventSource(`/chat?message=${encodeURIComponent(message)}`);

    // Render the user's message
    renderMessage(`You: ${message}`, "user-message");

    const assistantDiv = document.createElement("div");
    assistantDiv.className = "assistant-message chat-bubble";
    chatDisplay.appendChild(assistantDiv);

    let assistantMessage = ""; // Initialize a container for the full response

    typingIndicator.style.display = "block"; // Show typing indicator

    eventSource.onmessage = (event) => {
        try {
            const chunk = event.data.trim(); // Plain text chunk
            console.log("Chunk received:", chunk);

            if (chunk === "[END]") {
                console.log("Streaming ended.");
                eventSource.close();
                typingIndicator.style.display = "none"; // Hide typing indicator
                return;
            }

            assistantMessage += chunk + " "; // Append the chunk
            assistantDiv.innerHTML = assistantMessage.replace(/\n/g, "<br>").trim();
            chatDisplay.scrollTop = chatDisplay.scrollHeight; // Scroll to the bottom
        } catch (e) {
            console.error("Error processing chunk:", e);
            assistantDiv.innerHTML += "\n[Error: Invalid response format]";
        }
    };

    eventSource.onerror = () => {
        console.error("Connection lost while streaming response.");
        assistantDiv.innerHTML += "\n[Error: Unable to connect to the server]";
        typingIndicator.style.display = "none"; // Hide typing indicator
        eventSource.close();
    };

    input.value = ""; // Clear input
    input.focus(); // Refocus input
};

const renderMessage = (message, type) => {
    const div = document.createElement("div");
    div.className = `${type} chat-bubble`;
    div.textContent = message;
    chatDisplay.appendChild(div);

    // Auto-scroll to the latest message
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
};

const handleSendMessage = () => {
    const message = input.value.trim();
    if (!message) {
        alert("Please type a message before sending.");
        return;
    }
    streamResponse(message);
};

const toggleDarkMode = () => {
    document.body.classList.toggle("bg-dark");
    document.body.classList.toggle("text-light");
    chatDisplay.classList.toggle("bg-secondary");
    chatDisplay.classList.toggle("text-light");

    // Adjust chat bubble colors in dark mode
    const userMessages = document.querySelectorAll(".user-message");
    const assistantMessages = document.querySelectorAll(".assistant-message");

    userMessages.forEach((bubble) => {
        bubble.classList.toggle("bg-dark");
    });

    assistantMessages.forEach((bubble) => {
        bubble.classList.toggle("bg-dark");
    });
};


