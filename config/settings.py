import os
from pathlib import Path
from dotenv import load_dotenv

# Diretório Base do Projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega as variáveis do arquivo .env, se existir
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Configurações do Banco de Dados PostgreSQL
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "patrimonio_db")

# Se o arquivo .env existir, prioriza PostgreSQL, caso contrário usa SQLite
if env_path.exists():
    DEFAULT_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DEFAULT_DB_URL = "sqlite:///patrimonio.db"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Diretório para armazenamento físico de anexos
ATTACHMENTS_DIR = BASE_DIR / "assets" / "attachments"
ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)

# Diretório de logs
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
