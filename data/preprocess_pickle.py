import os
import pickle
import re
import sys

from tqdm import tqdm

data = os.path.dirname(__file__)
pickle_path = os.path.join(data, "final_result.pkl")
new_pickle_path = os.path.join(data, "data.pkl")
embedded_pickle_path = os.path.join(data, "embedded_data.pkl")

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)
from data.db_manager import create_vector_index
from data.embeddings import embed_question


def load_pickle(path: str = pickle_path) -> dict:
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data


def save_pickle(data: list[dict], path: str = new_pickle_path) -> None:
    with open(path, "wb") as f:
        pickle.dump(data, f)


postfix = "\n위 도움말이 도움이 되었나요?\n"
optional_postfix = "\n관련 도움말/키워드\n"
len_optional_postfix = len(optional_postfix)


def process_postfix(text: str) -> dict:
    answer = ""
    index = text.index(postfix)
    answer = text[:index].strip()

    try:
        optional_postfix_index = text.index(optional_postfix)
        optional = text[optional_postfix_index + len_optional_postfix :]
        optional = [*optional.strip().split("\n")]
        if "" in optional:
            empty_idx = optional.index("")
            optional = optional[:empty_idx]
        return {"answer": answer, "optional": optional}
    except ValueError:
        # '관련 도움말/키워드'가 없는 경우
        return {"answer": answer, "optional": []}


def replace_non_breaking_space(text: str) -> str:
    """
    \xa0: non-breaking space
    반복되는 non-breaking space를 하나의 공백문자로 대체
    """
    return re.sub("\xa0+", " ", text)


def preprocess() -> dict[str, dict[str, str | list[str]]]:
    data: dict = load_pickle()
    preprocessed_data = dict()

    for key, value in data.items():
        key: str = replace_non_breaking_space(key)
        value: str = replace_non_breaking_space(value)
        res: dict = process_postfix(value)
        preprocessed_data[key] = res

    save_pickle(data=preprocessed_data, path=new_pickle_path)
    return preprocessed_data


def embed_pickle():
    data = load_pickle(new_pickle_path)
    embedded_data: list[dict[str, int | str | list[float]]] = []
    questions = list(data.keys())
    for i, question in enumerate(tqdm(questions)):
        try:
            embedding = embed_question(question)
            embedded_data.append(
                {
                    "id": i + 1,
                    "question": question,
                    "answer": data[question]["answer"],
                    "optional": data[question]["optional"],
                    "vector": embedding,
                }
            )
        except ValueError:
            print(f"Failed to embed question: {question}")
            continue
    save_pickle(data=embedded_data, path=embedded_pickle_path)
    return embedded_data


if __name__ == "__main__":
    preprocess()  # 전처리 후 data.pkl에 저장
    """
    저장되는 데이터 예시
    {
        "질문 1": {"answer": "답변 1", "optional": ["키워드 1", "키워드 2"]},
        "질문 2": {"answer": "답변 2", "optional": []}
    }
    """
    # data = load_pickle(new_pickle_path)
    # print(data)

    embedded_pickle = embed_pickle()  # data.pkl의 질문을 임베딩하여
    create_vector_index(data=embedded_pickle)  # milvus에 저장
