from controllers.base_controller import BaseController
from services.employee_service import EmployeeService
from utils.exceptions import BusinessRuleException

class EmployeeController(BaseController):
    def __init__(self, db):
        super().__init__(db)
        self.service = EmployeeService(db)

    def list_employees(self):
        """Retorna a lista de todos os funcionários."""
        try:
            return self.service.get_all_employees()
        except Exception:
            return []

    def create_employee(self, name: str, sector_id: int):
        """Tenta cadastrar um novo funcionário e trata exceções de negócio."""
        try:
            employee = self.service.create_employee(name, sector_id)
            return True, employee
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    def delete_employee(self, employee_id: int):
        """Tenta remover um funcionário após verificar se ele não possui bens sob posse ativa."""
        try:
            self.service.delete_employee(employee_id)
            return True, "Funcionário excluído com sucesso."
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"
