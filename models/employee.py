from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Employee(Base):
    __tablename__ = "funcionarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    setor_id = Column(Integer, ForeignKey("setores.id", ondelete="RESTRICT"), nullable=False)

    # Relacionamentos
    sector = relationship("Sector", back_populates="employees")
    assets = relationship("Asset", back_populates="employee")

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, nome='{self.nome}', sector_id={self.setor_id})>"
