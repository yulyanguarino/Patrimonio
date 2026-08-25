import os
from pathlib import Path
from dotenv import load_dotenv

# Aponta para a branch "dev" do Neon (banco Postgres separado da produção).
# Os dados persistem normalmente entre execuções — sem reset automático.
# Pra zerar a branch dev quando quiser, rode scripts/reset_dev_db.py manualmente.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
os.environ["DATABASE_URL"] = os.environ["NEON_DEV_DATABASE_URL"]

from database.init_db import init_database
import flet as ft
from main import main

if __name__ == "__main__":
    print("=" * 60)
    print("INICIANDO O SISTEMA EM MODO DE TESTE / SANDBOX")
    print("Banco de dados: branch 'dev' do Neon (isolada da produção)")
    print("=" * 60)

    # Garante que as tabelas e dados padrão existam (idempotente)
    init_database()

    # Executa a aplicação gráfica em ambiente de teste
    ft.run(main)
