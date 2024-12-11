import os
from pathlib import Path
import openai
from dotenv import load_dotenv

load_dotenv(override=True)

CHAT_MODEL = os.getenv("CHAT_MODEL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
client = openai.OpenAI()

root_dir = Path(__file__).resolve().parent.parent
prompts_dir = Path.joinpath(root_dir, "prompts")
chat_system_prompt_path = Path.joinpath(prompts_dir, "chat_system_prompt.txt")

if __name__ == "__main__":

    def get_response_stream(prompt):
        stream = client.chat.completions.create(
            model=CHAT_MODEL, messages=[{"role": "user", "content": prompt}], stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def print_response_stream(prompt):
        for response in get_response_stream(prompt):
            print(response, end="", flush=True)

    print_response_stream("안녕! 반가워")
