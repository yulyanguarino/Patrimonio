from controllers.base_controller import BaseController
from services.category_service import CategoryService
from utils.exceptions import BusinessRuleException

class CategoryController(BaseController):
    def __init__(self, db):
        super().__init__(db)
        self.service = CategoryService(db)

    def list_categories(self):
        """Retorna a lista de todas as categorias."""
        try:
            return self.service.get_all_categories()
        except Exception:
            return []

    def create_category(self, name: str):
        """Tenta cadastrar uma nova categoria e trata exceções de negócio."""
        try:
            category = self.service.create_category(name)
            return True, category
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    def update_category(self, category_id: int, name: str):
        """Tenta atualizar o nome de uma categoria e trata exceções de negócio."""
        try:
            category = self.service.update_category(category_id, name)
            return True, category
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    def delete_category(self, category_id: int):
        """Tenta remover uma categoria após validação de dependências."""
        try:
            self.service.delete_category(category_id)
            return True, "Categoria excluída com sucesso."
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"
