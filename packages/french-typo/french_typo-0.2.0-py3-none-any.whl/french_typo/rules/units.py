import re

def normalize_units(text: str) -> str:
    text = re.sub(r"\b(KM|Km|kms|KMS)\b", "km", text)
    text = re.sub(r"\b(KG|Kg|kgs|KGS)\b", "kg", text)
    text = re.sub(r"\bkm/h\b", "km/h", text, flags=re.IGNORECASE)
    text = re.sub(r"\bkg/m3\b", "kg/m³", text, flags=re.IGNORECASE)
    return text
