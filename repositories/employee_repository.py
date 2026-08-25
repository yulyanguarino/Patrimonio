from typing import List
from sqlalchemy.orm import Session
from models.employee import Employee
from repositories.base_repository import BaseRepository

class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self, db: Session):
        super().__init__(Employee, db)

    def get_by_sector(self, sector_id: int) -> List[Employee]:
        """Retorna a lista de funcionários alocados em um determinado setor."""
        return self.db.query(Employee).filter(Employee.setor_id == sector_id).all()

    def get_by_name(self, name: str) -> Employee | None:
        """Busca funcionário por nome exato (ignora case)."""
        return self.db.query(Employee).filter(Employee.nome.ilike(name)).first()
