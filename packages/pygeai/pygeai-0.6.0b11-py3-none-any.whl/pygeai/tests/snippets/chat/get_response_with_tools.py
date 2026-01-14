from pygeai.chat.clients import ChatClient

client = ChatClient()

model = "openai/o1-pro"
input_text = "What is the weather like in Paris today?"

tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current temperature for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country e.g. Paris, France"
                }
            },
            "required": ["location"],
            "additionalProperties": False
        }
    }
]

response = client.get_response(
    model=model,
    input=input_text,
    tools=tools,
    tool_choice="auto",
    temperature=1.0,
    reasoning={"effort": "medium"}
)

print(response)
