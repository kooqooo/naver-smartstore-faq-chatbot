import os

import pymilvus
from dotenv import load_dotenv

load_dotenv(override=True)
dimension = 1536 if os.getenv("EMBEDDING_MODEL").endswith("small") else 3072
db_path = os.path.join(os.path.dirname(__file__), "milvus.db")


if os.name == 'nt':                     # Windows
    client = pymilvus.MilvusClient()    # docker-compose가 실행중이어야 가능합니다.
else:
    client = pymilvus.MilvusClient(db_path)


def create_vector_index(collection_name: str="faq", data: list[dict]=None):
    if data is None:
        raise ValueError("data must be provided")
    if client.has_collection(collection_name=collection_name):
        print("이미 존재하는 collection이라서 새로 만들지 않습니다.")
        return None
    client.create_collection(collection_name=collection_name, dimension=dimension)
    client.insert(collection_name=collection_name, data=data)

def filter_by_threshold(search_results: list[list[dict]], threshold: float = 0.45):
    results = []
    for result in search_results[0]:
        if result["distance"] >= threshold:
            results.append(result)
    return results

def search_from_faq(embedded_question: list[float], collection_name: str="faq", limit: int=10) -> list[dict]:
    results = []
    searched_results: list[list[dict]] = client.search(collection_name=collection_name, data=[embedded_question], output_fields=["question", "answer", "optional"], limit=limit)
    searched_results = filter_by_threshold(searched_results, threshold=0.4)
    for result in searched_results:
        temp = dict()
        entity = result["entity"]
        # temp["id"] = result["id"]
        temp["question"] = entity["question"]
        temp["answer"] = entity["answer"]
        temp["optional"] = entity["optional"]
        results.append(temp)
    return results

if __name__ == "__main__":
    from openai import OpenAI
    openai = OpenAI()
    
    question = input("질문을 입력하세요: ")
    embedded_question = openai.embeddings.create(input=question, model="text-embedding-3-small").data[0].embedding

    collection_name = "faq"
    results: list[list[dict]] = client.search(collection_name=collection_name, data=[embedded_question], output_fields=["question", "answer", "optional"], limit=10)
    results = filter_by_threshold(results, threshold=0.4)

    print(f"\n사용자 질문 : {question}\n\n")
    for result in results:
        entity = result["entity"]
        print(f"검색된 질문 : #{result["id"]}# {entity['question']}")
        # print(f"답변 : {entity['answer']}")
        print(f"유사도 : {result['distance']}")
        print()
    