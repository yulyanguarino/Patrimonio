"""
Lê o CSV de inventário de hardware (formato "Name;Value", um arquivo por
máquina) gerado pelo script de coleta do usuário, e converte pros campos
usados no cadastro de patrimônio (Notebook/Computador).
"""
import csv

FIELD_LABELS = {
    "Nome_Computador": "Nome do Computador",
    "Usuario": "Usuário",
    "Windows": "Sistema Operacional",
    "Versao_Windows": "Versão do Windows",
    "Build": "Build",
    "Arquitetura": "Arquitetura",
    "Fabricante": "Fabricante",
    "Modelo": "Modelo",
    "CPU": "Processador",
    "RAM_GB": "Memória RAM (GB)",
    "RAM_Velocidade_MHz": "Velocidade da RAM (MHz)",
    "Placa_Mae": "Placa-Mãe",
    "BIOS_Fabricante": "Fabricante da BIOS",
    "BIOS_Versao": "Versão da BIOS",
    "BIOS_Data": "Data da BIOS",
    "Serial_Equipamento": "Número de Série",
    "Disco_Modelo": "Modelo do Disco",
    "Disco_Total_GB": "Disco Total (GB)",
    "Disco_Usado_GB": "Disco Usado (GB)",
    "Disco_Livre_GB": "Disco Livre (GB)",
    "Video": "Placa de Vídeo",
    "IP": "Endereço IP",
    "MAC": "Endereço MAC",
    "Dominio": "Domínio",
    "Data_Instalacao_Windows": "Instalação do Windows",
    "Ultimo_Boot": "Última Inicialização",
}


def parse_inventory_csv(path: str) -> dict:
    """Lê o CSV de inventário (cabeçalho Name;Value) e retorna {campo: valor}."""
    data = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        rows = list(reader)
    for row in rows[1:]:  # pula o cabeçalho "Name";"Value"
        if len(row) >= 2 and row[0].strip():
            data[row[0].strip()] = row[1].strip()
    return data


def build_asset_name(data: dict) -> str:
    """Monta o nome sugerido do patrimônio a partir do fabricante/modelo."""
    fabricante = data.get("Fabricante", "").strip()
    modelo = data.get("Modelo", "").strip()
    nome = f"{fabricante} {modelo}".strip()
    return nome or data.get("Nome_Computador", "Computador Importado")


def build_observacoes(data: dict) -> str:
    """Formata todos os campos reconhecidos como texto legível pras Observações."""
    lines = [
        f"{label}: {data[key]}"
        for key, label in FIELD_LABELS.items()
        if data.get(key)
    ]
    return "\n".join(lines)
