# Default chat settings
chat_settings = {
    "system_prompt": "You are a friendly and witty conversational assistant.",
    "temperature": 0.7,
    "param_1": "",
    "param_2": ""
}

def get_chat_settings():
    """
    Returns the current chat settings.
    """
    return chat_settings

def update_chat_settings(data):
    """
    Updates the chat settings based on the provided data.
    """
    for key, value in data.items():
        if key in chat_settings:
            chat_settings[key] = value
    return chat_settings
