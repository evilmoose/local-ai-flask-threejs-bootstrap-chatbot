const input = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");
const chatDisplay = document.getElementById("chat-display");
const typingIndicator = document.getElementById("typing-indicator");
const darkModeToggle = document.getElementById("dark-mode-toggle");
const systemPromptInput = document.getElementById("systemPrompt");
const temperatureInput = document.getElementById("temperature");
const param1Input = document.getElementById("param1");
const param2Input = document.getElementById("param2");

// Event listeners
document.addEventListener("DOMContentLoaded", () => {
    sendButton.addEventListener("click", handleSendMessage);
    darkModeToggle.addEventListener("click", toggleDarkMode);
    systemPromptInput.addEventListener("change", updateSettings);
    temperatureInput.addEventListener("change", updateSettings);
    param1Input.addEventListener("change", updateSettings);
    param2Input.addEventListener("change", updateSettings);

    // Fetch initial settings
    fetch("/settings")
        .then(response => response.json())
        .then(settings => {
            systemPromptInput.value = settings.system_prompt;
            temperatureInput.value = settings.temperature;
            param1Input.value = settings.param_1 || ""; // Default empty if undefined
            param2Input.value = settings.param_2 || ""; // Default empty if undefined
        })
        .catch(error => console.error("Error fetching settings:", error));

    // Simulate proactive message after a delay
    setTimeout(() => {
        renderProactiveMessage("Hi there! Just checking in. How’s your day going?");
    }, 30000); // Trigger proactive message after 30 seconds
});

const handleSendMessage = () => {
    const message = input.value.trim();
    if (!message) {
        alert("Please type a message before sending.");
        return;
    }
    streamResponse(message);
};

const streamResponse = (message) => {
    const eventSource = new EventSource(`/chat?message=${encodeURIComponent(message)}`);
    renderMessage(`You: ${message}`, "user-message");

    const assistantDiv = document.createElement("div");
    assistantDiv.className = "assistant-message chat-bubble";
    chatDisplay.appendChild(assistantDiv);

    let assistantMessage = "";
    typingIndicator.style.display = "block"; // Show typing indicator

    eventSource.onmessage = (event) => {
        const chunk = event.data.trim();
        if (chunk === "[END]") {
            typingIndicator.style.display = "none"; // Hide typing indicator
            eventSource.close(); // Close connection
            return;
        }

        assistantMessage += chunk + " ";
        assistantDiv.innerHTML = assistantMessage.replace(/\n/g, "<br>").trim();
        chatDisplay.scrollTop = chatDisplay.scrollHeight; // Auto-scroll
    };

    eventSource.onerror = (error) => {
        typingIndicator.style.display = "none"; // Hide typing indicator
        renderMessage("[Error: Unable to fetch a response from the server. Please try again.]", "error-message");
        eventSource.close(); // Close connection
    };

    input.value = "";
    input.focus();
};

let eventSource = null; // Declare globally to manage the connection

const connectProactiveMessages = () => {
    if (eventSource) {
        eventSource.close(); // Close existing connection if it exists
        console.log("DEBUG: Closed existing EventSource connection.");
    }

    eventSource = new EventSource("/proactive");

    eventSource.onmessage = (event) => {
        const message = event.data.trim();
        if (message && message !== "[END]") {
            renderProactiveMessage(message);
        }
    };

    eventSource.onerror = (error) => {
        console.error("Error in proactive message stream. Attempting to reconnect...");
        eventSource.close();

        // Reconnect after an error
        setTimeout(() => {
            connectProactiveMessages();
        }, 5000);
    };
};

window.addEventListener("beforeunload", () => {
    if (eventSource) {
        eventSource.close();
        console.log("DEBUG: EventSource connection closed on window unload.");
    }
});

connectProactiveMessages();


// Close SSE when user starts typing
const chatInput = document.getElementById("chat-input"); // Replace with your input field ID
chatInput.addEventListener("input", () => {
    if (eventSource) {
        console.log("User started typing. Closing proactive message stream...");
        eventSource.close();
        eventSource = null; // Clean up reference
    }
});

// Reconnect if needed (optional)
const reconnectProactiveMessages = () => {
    if (!eventSource) {
        console.log("Reconnecting proactive messages...");
        connectProactiveMessages();
    }
};

// Optionally, reconnect after a period of inactivity
let typingTimeout;

chatInput.addEventListener("input", () => {
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        reconnectProactiveMessages();
    }, 30000); // Reconnect after 30 seconds of no typing
});

// Initialize connection on page load
document.addEventListener("DOMContentLoaded", () => {
    connectProactiveMessages();
});


const renderProactiveMessage = (message) => {
    // Fallback if the message is null or not a string
    if (!message || typeof message !== "string") {
        message = "Hello! How can I assist you today?";
    }

    // Create a new div for the proactive message
    const div = document.createElement("div");
    div.className = "assistant-message proactive"; // Preserve original class names
    div.textContent = `Rebecca: ${message}`;

    // Ensure the chat display element exists
    if (chatDisplay) {
        chatDisplay.appendChild(div);
        chatDisplay.scrollTop = chatDisplay.scrollHeight; // Auto-scroll to the latest message
    } else {
        console.error("chatDisplay not found. Ensure it's defined in the DOM.");
    }
};



const updateSettings = () => {
    const currentSettings = {
        system_prompt: systemPromptInput.value,
        temperature: parseFloat(temperatureInput.value),
        param_1: param1Input.value,
        param_2: param2Input.value
    };
    fetch("/settings")
        .then(response => response.json())
        .then(existingSettings => {
            const changes = {};
            for (let key in currentSettings) {
                if (currentSettings[key] !== existingSettings[key]) {
                    changes[key] = currentSettings[key];
                }
            }
            if (Object.keys(changes).length > 0) {
                return fetch("/settings", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(changes)
                });
            }
        })
        .catch(error => console.error("Error updating settings:", error));
};

const toggleDarkMode = () => {
    document.body.classList.toggle("bg-dark");
    document.body.classList.toggle("text-light");
};

const renderMessage = (message, className) => {
    const div = document.createElement("div");
    div.className = className || "chat-bubble";
    div.innerHTML = message.replace(/\n/g, "<br>");
    chatDisplay.appendChild(div);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
};
