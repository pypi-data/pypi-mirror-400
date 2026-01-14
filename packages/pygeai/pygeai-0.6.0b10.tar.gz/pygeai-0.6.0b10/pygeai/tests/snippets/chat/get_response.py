from pygeai.chat.clients import ChatClient

client = ChatClient()

model = "openai/o1-pro"
input_text = "What is the weather like in Paris today?"

response = client.get_response(
    model=model,
    input=input_text,
    temperature=0.7,
    max_output_tokens=1000
)

print(response)
