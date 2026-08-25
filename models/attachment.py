from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from models.base import Base

class Attachment(Base):
    __tablename__ = "anexos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patrimonio_id = Column(Integer, ForeignKey("patrimonios.id", ondelete="CASCADE"), nullable=True, index=True)
    manutencao_id = Column(Integer, ForeignKey("manutencoes.id", ondelete="CASCADE"), nullable=True, index=True)
    nome_arquivo = Column(String(255), nullable=False)
    caminho_local = Column(String(512), nullable=False)
    tipo_documento = Column(String(50), nullable=False)  # 'Foto', 'Nota Fiscal', 'Manual', 'Garantia', 'Outros'
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)

    # Relacionamentos
    asset = relationship("Asset", back_populates="attachments")
    maintenance = relationship("Maintenance", back_populates="attachments")

    def __repr__(self) -> str:
        return f"<Attachment(id={self.id}, nome='{self.nome_arquivo}', tipo='{self.tipo_documento}')>"
