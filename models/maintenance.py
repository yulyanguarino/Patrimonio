from sqlalchemy import Column, Integer, String, Date, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Maintenance(Base):
    __tablename__ = "manutencoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patrimonio_id = Column(Integer, ForeignKey("patrimonios.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo = Column(String(30), nullable=False)  # 'Preventiva' ou 'Corretiva'
    data_manutencao = Column(Date, nullable=False)
    prestador = Column(String(150), nullable=False)
    descricao_problema = Column(Text, nullable=False)
    servico_executado = Column(Text, nullable=False)
    valor_gasto = Column(Numeric(10, 2), nullable=False)
    data_proxima = Column(Date, nullable=True)
    observacoes = Column(Text, nullable=True)

    # Relacionamentos
    asset = relationship("Asset", back_populates="maintenances")
    attachments = relationship("Attachment", back_populates="maintenance", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Maintenance(id={self.id}, patrimonio_id={self.patrimonio_id}, tipo='{self.tipo}', valor={self.valor_gasto})>"
