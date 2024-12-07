document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("chat-input");
    const sendButton = document.getElementById("send-button");
    const chatDisplay = document.getElementById("chat-display");

    const renderMessage = (message, type) => {
        const div = document.createElement("div");
        div.className = type;
        div.textContent = message;
        chatDisplay.appendChild(div);
    };

    sendButton.addEventListener("click", () => {
        const message = input.value.trim();
        if (!message) return;
        
        renderMessage(`You: ${message}`, "user-message");

        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.response) {
                    renderMessage(`Bot: ${data.response}`, "assistant-message");
                }
            });
        input.value = "";
    });
});
