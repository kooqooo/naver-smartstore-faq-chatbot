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
