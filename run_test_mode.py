import os
import sys
from pathlib import Path

# Força o uso do banco de dados SQLite de teste isolado
BASE_DIR = Path(__file__).resolve().parent
os.environ["DATABASE_URL"] = f"sqlite:///{BASE_DIR / 'patrimonio_teste.db'}"

from database.init_db import init_database
import flet as ft
from main import main

if __name__ == "__main__":
    print("=" * 60)
    print("INICIANDO O SISTEMA EM MODO DE TESTE / SANDBOX")
    print("Banco de dados de teste: patrimonio_teste.db")
    print("=" * 60)
    
    # Garante que as tabelas de teste e dados padrão estejam inicializados
    init_database()
    
    # Executa a aplicação gráfica em ambiente de teste
    ft.run(main)
