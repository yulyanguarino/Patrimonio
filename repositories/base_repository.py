from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.orm import Session
from models.base import Base

# Tipo genérico vinculado a instâncias herdadas da declarative Base
T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> Optional[T]:
        """Busca um registro pelo seu ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> List[T]:
        """Retorna todos os registros da tabela."""
        return self.db.query(self.model).all()

    def create(self, obj: T) -> T:
        """Adiciona um novo registro e confirma a transação."""
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except Exception:
            self.db.rollback()
            raise

    def update(self, obj: T) -> T:
        """Marca o objeto para atualização e confirma a transação."""
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except Exception:
            self.db.rollback()
            raise

    def delete(self, obj: T) -> None:
        """Remove o registro do contexto da sessão e confirma a transação."""
        try:
            self.db.delete(obj)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
