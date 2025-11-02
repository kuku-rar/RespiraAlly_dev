import os
from openai import OpenAI
from typing import Union, List
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def to_vector(text: Union[str, List[str]], normalize: bool = True) -> List[float]:
    if isinstance(text, str):
        inputs = [text]
    elif isinstance(text, list):
        inputs = text
    else:
        raise TypeError("輸入必須為 str 或 List[str]")

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=inputs
    )

    vectors = [r.embedding for r in response.data]

    if isinstance(text, str):
        return vectors[0]
    return vectors


def safe_to_vector(text, normalize: bool = True):
    try:
        return to_vector(text, normalize=normalize)
    except Exception as e:
        print(f"[embedding error] {e}")
        return []


