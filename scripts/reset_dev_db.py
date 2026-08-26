"""
Reset manual da branch 'dev' do Neon.

Roda SÓ quando você pedir (nunca é chamado automaticamente): apaga todas as
tabelas da branch dev e recria do zero (schema + seed), sem tocar na produção.

Uso:
    python scripts/reset_dev_db.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
os.environ["DATABASE_URL"] = os.environ["NEON_DEV_DATABASE_URL"]

from sqlalchemy import text
from config.database import engine
from models.base import Base
from database.init_db import init_database

if __name__ == "__main__":
    confirm = input("Isso vai APAGAR todos os dados da branch 'dev' do Neon. Confirma? (digite 'sim'): ")
    if confirm.strip().lower() != "sim":
        print("Cancelado.")
    else:
        print("Apagando tabelas da branch dev...")
        Base.metadata.drop_all(bind=engine)
        # A sequence do número patrimonial é um objeto separado das tabelas --
        # apagar as tabelas não reseta ela, então sem isso a numeração
        # continuaria de onde parou em vez de voltar pro 001.
        print("Reiniciando a numeração de patrimônios (sequence)...")
        with engine.connect() as conn:
            conn.execute(text("DROP SEQUENCE IF EXISTS numero_patrimonial_seq;"))
            conn.commit()
        print("Recriando schema e dados padrão...")
        init_database()
        print("Branch dev resetada com sucesso.")
