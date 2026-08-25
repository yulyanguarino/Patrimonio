from sqlalchemy.orm import Session
from models.sector import Sector
from repositories.base_repository import BaseRepository

class SectorRepository(BaseRepository[Sector]):
    def __init__(self, db: Session):
        super().__init__(Sector, db)

    def get_by_name(self, name: str) -> Sector | None:
        """Busca um setor pelo nome exato (ignora maiúsculas/minúsculas)."""
        return self.db.query(Sector).filter(Sector.nome.ilike(name)).first()
