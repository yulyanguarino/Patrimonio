from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from models.base import Base

class Asset(Base):
    __tablename__ = "patrimonios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_patrimonial = Column(String(30), unique=True, nullable=False, index=True)
    nome = Column(String(150), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="RESTRICT"), nullable=False)
    setor_id = Column(Integer, ForeignKey("setores.id", ondelete="RESTRICT"), nullable=False)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id", ondelete="RESTRICT"), nullable=True)
    data_compra = Column(Date, nullable=True)
    nota_fiscal = Column(String(100), nullable=True)
    garantia_meses = Column(Integer, nullable=True)
    status = Column(String(30), nullable=False, default="Disponível", index=True)
    observacoes = Column(Text, nullable=True)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    category = relationship("Category", back_populates="assets")
    sector = relationship("Sector", back_populates="assets")
    employee = relationship("Employee", back_populates="assets")
    maintenances = relationship("Maintenance", back_populates="asset", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="asset", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Asset(id={self.id}, numero='{self.numero_patrimonial}', nome='{self.nome}', status='{self.status}')>"
