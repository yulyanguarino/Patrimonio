from typing import List
from sqlalchemy.orm import Session
from models.sector import Sector
from repositories.sector_repository import SectorRepository
from utils.exceptions import BusinessRuleException

class SectorService:
    def __init__(self, db: Session):
        self.db = db
        self.sector_repo = SectorRepository(db)

    def create_sector(self, name: str) -> Sector:
        """Cadastra um novo setor com validações de unicidade e preenchimento."""
        name = name.strip()
        if not name:
            raise BusinessRuleException("O nome do setor não pode ser vazio.")
        
        # Valida unicidade de nome
        if self.sector_repo.get_by_name(name):
            raise BusinessRuleException(f"Já existe um setor cadastrado com o nome '{name}'.")
            
        sector = Sector(nome=name)
        return self.sector_repo.create(sector)

    def get_all_sectors(self) -> List[Sector]:
        """Retorna todos os setores cadastrados."""
        return self.sector_repo.get_all()

    def get_sector_by_id(self, sector_id: int) -> Sector | None:
        """Busca um setor por ID."""
        return self.sector_repo.get_by_id(sector_id)

    def delete_sector(self, sector_id: int) -> None:
        """Remove um setor do banco se não houver dependências vinculadas (funcionários ou patrimônios)."""
        sector = self.sector_repo.get_by_id(sector_id)
        if not sector:
            raise BusinessRuleException("Setor não encontrado.")
            
        # Validação de integridade referencial antes da exclusão
        if len(sector.employees) > 0:
            raise BusinessRuleException(
                f"Não é possível excluir o setor '{sector.nome}' "
                f"porque existem funcionários vinculados a ele."
            )
            
        if len(sector.assets) > 0:
            raise BusinessRuleException(
                f"Não é possível excluir o setor '{sector.nome}' "
                f"porque existem patrimônios alocados a ele."
            )
            
        self.sector_repo.delete(sector)
