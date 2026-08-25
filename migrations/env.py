import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Adiciona o diretório raiz do projeto ao path para importar as configurações e os modelos
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Importações internas do projeto
from config.settings import DATABASE_URL
from models.base import Base
# Importar os modelos explicitamente para que o metadata os registre
from models.sector import Sector
from models.category import Category
from models.employee import Employee
from models.asset import Asset
from models.maintenance import Maintenance
from models.attachment import Attachment

# Configuração do Alembic
config = context.config

# Injeta a URL de banco dinamicamente a partir de config.settings (carregada do .env)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Configura o log conforme definido no alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Configura o target_metadata para suporte a autogerador de migrations
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Executa as migrações em modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "pyformat"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Executa as migrações em modo 'online' (conectado ao banco)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
