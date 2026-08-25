from typing import List, Dict
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from models.asset import Asset
from repositories.base_repository import BaseRepository

class AssetRepository(BaseRepository[Asset]):
    def __init__(self, db: Session):
        super().__init__(Asset, db)

    def get_next_sequence_value(self) -> int:
        """
        Obtém o próximo valor inteiro da Sequence 'numero_patrimonial_seq'
        garantindo integridade concorrente. Em caso de testes usando SQLite,
        utiliza uma lógica simulada compatível.
        """
        if self.db.bind.dialect.name == "sqlite":
            # Fallback seguro para testes unitários em SQLite
            # Como SQLite é single-thread nos testes, max(id) + 1 é suficiente
            max_val = self.db.query(func.max(Asset.id)).scalar()
            return (max_val or 0) + 1
            
        result = self.db.execute(text("SELECT nextval('numero_patrimonial_seq')"))
        return result.scalar()

    def get_by_number(self, number: str) -> Asset | None:
        """Busca um patrimônio pelo seu número patrimonial exato."""
        return self.db.query(Asset).filter(Asset.numero_patrimonial == number).first()

    def search_assets(
        self,
        query_text: str | None = None,
        category_id: int | None = None,
        sector_id: int | None = None,
        status: str | None = None
    ) -> List[Asset]:
        """
        Consulta avançada de patrimônios aplicando filtros opcionais e pesquisa textual 
        sobre o nome do bem, número patrimonial, categoria, setor ou responsável.
        """
        from models.category import Category
        from models.sector import Sector
        from models.employee import Employee
        from sqlalchemy import or_, func

        q = self.db.query(Asset).outerjoin(Asset.category).outerjoin(Asset.sector).outerjoin(Asset.employee)
        
        if query_text:
            clean_query = query_text.strip().lower()
            if clean_query:
                search_pattern = f"%{clean_query}%"
                q = q.filter(
                    or_(
                        func.lower(Asset.nome).like(search_pattern),
                        func.lower(Asset.numero_patrimonial).like(search_pattern),
                        func.lower(Category.nome).like(search_pattern),
                        func.lower(Sector.nome).like(search_pattern),
                        func.lower(Employee.nome).like(search_pattern)
                    )
                )
            
        if category_id is not None:
            q = q.filter(Asset.categoria_id == category_id)
            
        if sector_id is not None:
            q = q.filter(Asset.setor_id == sector_id)
            
        if status:
            q = q.filter(Asset.status == status)
            
        return q.order_by(Asset.numero_patrimonial.asc()).all()

    def get_dashboard_metrics(self) -> Dict[str, int]:
        """
        Retorna as métricas de contagem de patrimônios consolidadas por status.
        """
        results = (
            self.db.query(Asset.status, func.count(Asset.id))
            .group_by(Asset.status)
            .all()
        )
        
        metrics = {
            "Total": self.db.query(func.count(Asset.id)).scalar() or 0,
            "Disponível": 0,
            "Em uso": 0,
            "Em manutenção": 0,
            "Baixado": 0
        }
        
        for status, count in results:
            metrics[status] = count
            
        return metrics

    def get_assets_by_sector_summary(self) -> List[tuple]:
        """Retorna contagem de patrimônios agrupados por setor."""
        from models.sector import Sector
        return (
            self.db.query(Sector.nome, func.count(Asset.id))
            .join(Asset, Asset.setor_id == Sector.id)
            .group_by(Sector.nome)
            .all()
        )

    def get_assets_by_category_summary(self) -> List[tuple]:
        """Retorna contagem de patrimônios agrupados por categoria."""
        from models.category import Category
        return (
            self.db.query(Category.nome, func.count(Asset.id))
            .join(Asset, Asset.categoria_id == Category.id)
            .group_by(Category.nome)
            .all()
        )
