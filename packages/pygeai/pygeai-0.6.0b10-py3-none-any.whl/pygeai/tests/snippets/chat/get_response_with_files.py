from pygeai.chat.clients import ChatClient

client = ChatClient()

model = "openai/o1-pro"
input_text = "Please analyze this image and describe what you see"
files = ["files/image.svg", "files/document.pdf"]

response = client.get_response(
    model=model,
    input=input_text,
    files=files,
    temperature=0.7
)

print(response)
