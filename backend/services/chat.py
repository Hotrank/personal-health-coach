from typing import Generator

import ollama


def stream_chat_response(user_input: str) -> Generator[str, None, None]:

    for chunk in ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": user_input}],
        stream=True,
    ):
        yield chunk["message"]["content"]