from datetime import date, datetime
from decimal import Decimal

def format_currency(value: float | Decimal | None) -> str:
    """Formata valores numéricos para o padrão de moeda brasileiro (R$ 1.250,00)."""
    if value is None:
        return "R$ 0,00"
    
    try:
        val = float(value)
    except (ValueError, TypeError):
        return "R$ 0,00"
        
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_date(d: date | datetime | None) -> str:
    """Formata datas do Python para o padrão brasileiro (DD/MM/AAAA)."""
    if d is None:
        return "-"
    
    if isinstance(d, datetime):
        return d.strftime("%d/%m/%Y %H:%M")
        
    return d.strftime("%d/%m/%Y")

def parse_date(date_str: str) -> date | None:
    """Tenta converter uma string formatada (DD/MM/AAAA) em um objeto date."""
    date_str = date_str.strip()
    if not date_str:
        return None
        
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
            
    return None
