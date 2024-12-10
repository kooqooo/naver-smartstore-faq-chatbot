import os

import pymilvus
from dotenv import load_dotenv

load_dotenv(override=True)
dimension = 1536 if os.getenv("EMBEDDING_MODEL").endswith("small") else 3072
db_path = os.path.join(os.path.dirname(__file__), "milvus.db")


client = pymilvus.MilvusClient(db_path)
if os.name == 'nt':
    client = pymilvus.MilvusClient() # docker-compose가 실행중이어야 가능합니다.


def create_vector_index(collection_name: str="faq", data: list[dict]=None):
    if data is None:
        raise ValueError("data must be provided")
    client.create_collection(collection_name=collection_name, dimension=dimension)
    client.insert(collection_name=collection_name, data=data)


if __name__ == "__main__":
    from preprocess_pickle import load_pickle
    
    embedded_pickle_path = os.path.join(os.path.dirname(__file__), "embedded_data.pkl")
    data = load_pickle(embedded_pickle_path)

    create_vector_index(data=data)
