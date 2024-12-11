import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

from src.config import EMBEDDING_MODEL
from src.config import client as openai_client

dimensions = 1536 if EMBEDDING_MODEL.endswith("small") else 3072


def embed_question(question: str) -> list[float]:
    # 임베딩
    embedding_response = openai_client.embeddings.create(
        input=question, model=EMBEDDING_MODEL, dimensions=dimensions
    )
    data = embedding_response.data[0]
    embedding = data.embedding
    return embedding


def embed_questions(questions: list[str]) -> list[list[float]]:
    # 임베딩
    embeddings = []
    embedding_response = openai_client.embeddings.create(
        input=questions, model=EMBEDDING_MODEL, dimensions=dimensions
    )
    data = embedding_response.data
    for d in data:
        embedding = d.embedding
        embeddings.append(embedding)
    return embeddings


if __name__ == "__main__":
    """
    # 임베딩 테스트
    result = openai_client.embeddings.create(input='hello world', model=EMBEDDING_MODEL, dimensions=dimensions)

    data = result.data[0]
    embedding: list[float] = data.embedding
    dimensions: int = len(embedding)
    print(f'임베딩 차원 : {dimensions}')
    """

    embeddings = embed_questions(["안녕하세요", "반가워요"])
    print(embeddings)
