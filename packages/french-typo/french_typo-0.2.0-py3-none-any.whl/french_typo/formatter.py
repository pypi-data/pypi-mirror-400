from french_typo.rules import (
    normalize_spaces,
    normalize_units,
    normalize_numbers,
)

def format_text(text: str) -> str:
    """
    Applique des règles typographiques françaises
    indépendantes de tout format.
    """
    text = normalize_spaces(text)
    text = normalize_units(text)
    text = normalize_numbers(text)
    return text
