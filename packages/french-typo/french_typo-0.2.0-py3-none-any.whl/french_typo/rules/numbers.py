import re

def normalize_numbers(text: str) -> str:
    """
    Normalise les ordinaux français sans rendu :
    - 1er, 2e, 2d, 3e
    - n°
    """
    return re.sub(
        r"\b(\d+)(er|e|d)\b",
        r"\1\2",
        text,
        flags=re.IGNORECASE,
    )
