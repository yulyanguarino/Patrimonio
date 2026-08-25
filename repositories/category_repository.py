from sqlalchemy.orm import Session
from models.category import Category
from repositories.base_repository import BaseRepository

class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(Category, db)

    def get_by_name(self, name: str) -> Category | None:
        """Busca uma categoria pelo nome exato (ignora maiúsculas/minúsculas)."""
        return self.db.query(Category).filter(Category.nome.ilike(name)).first()
