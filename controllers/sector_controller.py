from controllers.base_controller import BaseController
from services.sector_service import SectorService
from utils.exceptions import BusinessRuleException

class SectorController(BaseController):
    def __init__(self, db):
        super().__init__(db)
        self.service = SectorService(db)

    def list_sectors(self):
        """Retorna a lista de todos os setores."""
        try:
            return self.service.get_all_sectors()
        except Exception:
            return []

    def create_sector(self, name: str):
        """Tenta cadastrar um novo setor e trata exceções de negócio."""
        try:
            sector = self.service.create_sector(name)
            return True, sector
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    def delete_sector(self, sector_id: int):
        """Tenta remover um setor após validação de dependências."""
        try:
            self.service.delete_sector(sector_id)
            return True, "Setor excluído com sucesso."
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"
