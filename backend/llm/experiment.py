from ollama import chat

stream = chat(
    model="llama3.2",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant. The user's name is Heming. His cholesterol is high, and he is 40 years old. He is a software engineer.",
        },
        {
            "role": "user",
            "content": "what's my name? Any health advice you can give me?",
        },
    ],
    stream=True,
)
# Print the response as it arrives

# for chunk in stream:
#     print(chunk["message"]["content"], end="", flush=True)


from dotenv import load_dotenv

from backend.llm.openai_client import OpenAIClient

load_dotenv(dotenv_path="dev.env")

client = OpenAIClient(model="gpt-4o")
response = client.stream(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant. The user's name is Heming. His cholesterol is high, and he is 40 years old. He is a software engineer.",
        },
        {
            "role": "user",
            "content": "what's my name? ",
        },
    ]
)
for chunk in response:
    print(chunk, end="", flush=True)
