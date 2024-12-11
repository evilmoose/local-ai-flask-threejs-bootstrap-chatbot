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
    typingIndicator.style.display = "block";

    eventSource.onmessage = (event) => {
        const chunk = event.data.trim();
        if (chunk === "[END]") {
            typingIndicator.style.display = "none";
            eventSource.close();
            return;
        }
        assistantMessage += chunk + " ";
        assistantDiv.innerHTML = assistantMessage.replace(/\n/g, "<br>").trim();
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    };

    eventSource.onerror = (error) => {
        typingIndicator.style.display = "none";
        assistantDiv.innerHTML += "\n[Error: Unable to connect to the server]";
        eventSource.close();
    };

    input.value = "";
    input.focus();
};

const renderProactiveMessage = (message) => {
    const div = document.createElement("div");
    div.className = "assistant-message proactive";
    div.textContent = `Rebecca: ${message}`;
    chatDisplay.appendChild(div);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
};

const updateSettings = () => {
    const newSettings = {
        system_prompt: systemPromptInput.value,
        temperature: parseFloat(temperatureInput.value),
        param_1: param1Input.value,
        param_2: param2Input.value
    };

    fetch("/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newSettings)
    })
        .then(response => response.json())
        .then(updatedSettings => {
            console.log("Settings updated:", updatedSettings);
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
