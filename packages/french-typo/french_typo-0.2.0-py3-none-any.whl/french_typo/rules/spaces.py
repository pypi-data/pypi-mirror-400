import re

def normalize_spaces(text: str) -> str:
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"[ \t]+\.", ".", text)
    text = re.sub(r"(?m)^[ \t]+", "", text)
    text = re.sub(r"[ \t]+$", "", text)
    return text
