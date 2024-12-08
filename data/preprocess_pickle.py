import os
import re
import pickle


pickle_path = os.path.join(os.path.dirname(__file__), 'final_result.pkl')
new_pickle_path = os.path.join(os.path.dirname(__file__), 'data.pkl')

def load_pickle():
    with open(pickle_path, 'rb') as f:
        data = pickle.load(f)
    return data

def save_pickle(data: list[dict]):
    with open(new_pickle_path, 'wb') as f:
        pickle.dump(data, f)


postfix = "\n위 도움말이 도움이 되었나요?\n"
optional_postfix = "\n관련 도움말/키워드\n"
len_optional_postfix = len(optional_postfix)

def process_postfix(text: str) -> dict:
    res = {
        "answer": None,
        "optional": []
    }
    
    index = text.index(postfix)
    optional_text = ""
    res["answer"] = text[:index].strip()
    try:
        optional_postfix_index = text.index(optional_postfix)
        optional_text = text[optional_postfix_index + len_optional_postfix:]
        optional_text = [*optional_text.strip().split('\n')]
        if '' in optional_text:
            empty_idx = optional_text.index('')
            optional_text = optional_text[:empty_idx]
        res["optional"] = optional_text
    except ValueError: 
        # '관련 도움말/키워드'가 없는 경우
        return res
    return res
    
def replace_non_breaking_space(text: str) -> str:
    """
    \xa0: non-breaking space
    반복되는 non-breaking space를 하나의 공백문자로 대체
    """
    return re.sub('\xa0+', ' ', text)

def main() -> list[dict]:
    data: dict = load_pickle()
    preprocessed_data = []

    for key, value in data.items():
        value: str = replace_non_breaking_space(value)
        res: dict = process_postfix(value)
        res["question"] = key
        preprocessed_data.append(res)

    save_pickle(preprocessed_data)
    

if __name__ == '__main__':
    main()
