import ollama

convo = []

def stream_response(prompt):
    convo.append({'role': 'user', 'content': prompt})
    response = ''
    stream = ollama.chat(model='llama3.2', messages=convo, stream=True)
    print('\nASSISTANT:')

    try:
        for chunk in stream:
            content = chunk.get('message', {}).get('content', '')
            response += content
            print(content, end='', flush=True)
    except Exception as e:
        print("Error while processing stream:", e)


    print('\n')
    convo.append({'role': 'assistant', 'content': response})

while True:
    prompt = input('USER: \n')
    stream_response(prompt=prompt)