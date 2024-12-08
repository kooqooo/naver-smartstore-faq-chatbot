import os

import openai
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("MODEL")
client = openai.OpenAI()


if __name__ == "__main__":

    def get_response_stream(prompt):
        stream = client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": prompt}], stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def print_response_stream(prompt):
        for response in get_response_stream(prompt):
            print(response, end="", flush=True)

    print_response_stream("안녕! 반가워")
