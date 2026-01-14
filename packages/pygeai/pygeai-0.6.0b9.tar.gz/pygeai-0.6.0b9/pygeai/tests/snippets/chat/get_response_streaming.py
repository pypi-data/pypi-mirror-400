from pygeai.chat.clients import ChatClient

client = ChatClient()

model = "openai/o1-pro"
input_text = "Tell me a short story about a robot"

response = client.get_response(
    model=model,
    input=input_text,
    stream=True,
    temperature=0.7,
    max_output_tokens=500
)

print("Streaming response:")
for chunk in response:
    print(chunk, end='', flush=True)

print("\n\nStreaming complete!")
