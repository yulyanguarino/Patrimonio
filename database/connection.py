from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from config.database import SessionLocal

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager que fornece uma sessão de banco de dados.
    Garante o fechamento automático da conexão e executa commit automático,
    ou rollback em caso de qualquer exceção interna.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
