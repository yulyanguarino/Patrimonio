from typing import List
from sqlalchemy.orm import Session
from models.employee import Employee
from repositories.employee_repository import EmployeeRepository
from repositories.sector_repository import SectorRepository
from utils.exceptions import BusinessRuleException

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.employee_repo = EmployeeRepository(db)
        self.sector_repo = SectorRepository(db)

    def create_employee(self, name: str, sector_id: int) -> Employee:
        """Cadastra um novo funcionário vinculado a um setor ativo."""
        name = name.strip()
        if not name:
            raise BusinessRuleException("O nome do funcionário não pode ser vazio.")
        
        # Verifica se o setor existe
        sector = self.sector_repo.get_by_id(sector_id)
        if not sector:
            raise BusinessRuleException("O setor selecionado é inválido ou não existe.")
            
        employee = Employee(nome=name, setor_id=sector_id)
        return self.employee_repo.create(employee)

    def get_all_employees(self) -> List[Employee]:
        """Retorna todos os funcionários."""
        return self.employee_repo.get_all()

    def get_employee_by_id(self, employee_id: int) -> Employee | None:
        """Busca funcionário por ID."""
        return self.employee_repo.get_by_id(employee_id)

    def delete_employee(self, employee_id: int) -> None:
        """
        Exclui um funcionário se ele não for o responsável ativo por nenhum patrimônio.
        Desvincula o funcionário de bens inativos (como Disponível ou Em manutenção).
        """
        employee = self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise BusinessRuleException("Funcionário não encontrado.")
            
        # Verifica se há patrimônios sob a posse ativa ("Em uso") do funcionário
        active_assets = [a for a in employee.assets if a.status == "Em uso"]
        if active_assets:
            codes = ", ".join([a.numero_patrimonial for a in active_assets])
            raise BusinessRuleException(
                f"Não é possível excluir o funcionário '{employee.nome}' porque ele "
                f"é o responsável atual pelos patrimônios em uso: {codes}."
            )
            
        # Desvincula com segurança de patrimônios inativos (Disponíveis ou Em manutenção) antes de excluir
        for asset in employee.assets:
            asset.funcionario_id = None
            
        self.employee_repo.delete(employee)
