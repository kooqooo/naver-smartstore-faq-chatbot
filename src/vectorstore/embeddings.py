from src.config import EMBEDDING_MODEL, client as openai_client

if __name__ == "__main__":
    dimensions = 1536 if EMBEDDING_MODEL.endswith('small') else 3072
    result = openai_client.embeddings.create(input='hello world', model=EMBEDDING_MODEL, dimensions=dimensions)

    data = result.data[0]
    embedding = data.embedding
    dimensions = len(embedding)
