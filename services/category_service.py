from typing import List
from sqlalchemy.orm import Session
from models.category import Category
from repositories.category_repository import CategoryRepository
from utils.exceptions import BusinessRuleException

class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.category_repo = CategoryRepository(db)

    def create_category(self, name: str) -> Category:
        """Cadastra uma nova categoria de patrimônio com validações."""
        name = name.strip()
        if not name:
            raise BusinessRuleException("O nome da categoria não pode ser vazio.")
        
        # Valida unicidade de nome
        if self.category_repo.get_by_name(name):
            raise BusinessRuleException(f"Já existe uma categoria cadastrada com o nome '{name}'.")
            
        category = Category(nome=name)
        return self.category_repo.create(category)

    def get_all_categories(self) -> List[Category]:
        """Retorna todas as categorias."""
        return self.category_repo.get_all()

    def get_category_by_id(self, category_id: int) -> Category | None:
        """Busca categoria por ID."""
        return self.category_repo.get_by_id(category_id)

    def delete_category(self, category_id: int) -> None:
        """Remove a categoria se não houver nenhum patrimônio vinculado."""
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise BusinessRuleException("Categoria não encontrada.")
            
        # Validação de integridade referencial antes da exclusão
        if len(category.assets) > 0:
            raise BusinessRuleException(
                f"Não é possível excluir a categoria '{category.nome}' "
                f"porque existem patrimônios vinculados a ela."
            )
            
        self.category_repo.delete(category)
