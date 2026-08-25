from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base

class Category(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False)

    # Relacionamentos
    assets = relationship("Asset", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, nome='{self.nome}')>"
