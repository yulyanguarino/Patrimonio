import re

def is_empty(text: str | None) -> bool:
    """Verifica se uma string está vazia ou contém apenas espaços em branco."""
    return not text or not text.strip()

def is_valid_currency(text: str | None) -> bool:
    """Verifica se o formato numérico monetário informado é válido (ex: 150.00 ou 150,00 ou 150)."""
    if not text:
        return False
    text = text.strip()
    # Regex aceita números inteiros ou com 2 casas decimais separadas por ponto ou vírgula
    return bool(re.match(r"^\d+([.,]\d{1,2})?$", text))

def clean_currency_string(text: str) -> float:
    """Converte valores limpos pelo validador em float pronto para persistência."""
    clean_text = text.strip().replace(".", "").replace(",", ".")
    return float(clean_text)
