import os
import pickle
import re

pickle_path = os.path.join(os.path.dirname(__file__), "final_result.pkl")
new_pickle_path = os.path.join(os.path.dirname(__file__), "data.pkl")


def load_pickle(path: str = pickle_path) -> dict:
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data


def save_pickle(data: list[dict]):
    with open(new_pickle_path, "wb") as f:
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


def main() -> dict[str, dict[str, str | list[str]]]:
    data: dict = load_pickle()
    preprocessed_data = dict()

    for key, value in data.items():
        value: str = replace_non_breaking_space(value)
        res: dict = process_postfix(value)
        print(res)
        preprocessed_data[key] = (res)

    save_pickle(preprocessed_data)


if __name__ == "__main__":
    main()

    data = load_pickle(new_pickle_path)
    print(data)
    """
    저장되는 데이터 예시
    {
        "질문 1": {"answer": "답변 1", "optional": ["키워드 1", "키워드 2"]},
        "질문 2": {"answer": "답변 2", "optional": []}
    }
    """