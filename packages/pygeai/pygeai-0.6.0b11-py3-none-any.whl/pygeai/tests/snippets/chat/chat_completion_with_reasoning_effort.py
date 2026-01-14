from pygeai.chat.clients import ChatClient

client = ChatClient()

messages = [
    {
        "role": "user",
        "content": "Explain quantum computing in simple terms"
    }
]

response = client.chat_completion(
    model="openai/gpt-4o",
    messages=messages,
    reasoning_effort="high"
)

print(response)
