from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base

class Sector(Base):
    __tablename__ = "setores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False)

    # Relacionamentos
    # Excluir um setor apaga seus funcionários em cascata no ORM, mas RESTRICT em banco previne órfãos
    employees = relationship("Employee", back_populates="sector", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="sector")

    def __repr__(self) -> str:
        return f"<Sector(id={self.id}, nome='{self.nome}')>"
