from typing import List
from datetime import date
from sqlalchemy.orm import Session
from models.maintenance import Maintenance
from repositories.base_repository import BaseRepository

class MaintenanceRepository(BaseRepository[Maintenance]):
    def __init__(self, db: Session):
        super().__init__(Maintenance, db)

    def get_by_asset_id(self, asset_id: int) -> List[Maintenance]:
        """Busca o histórico de manutenções de um patrimônio específico ordenado por data descendente."""
        return (
            self.db.query(Maintenance)
            .filter(Maintenance.patrimonio_id == asset_id)
            .order_by(Maintenance.data_manutencao.desc())
            .all()
        )

    def filter_maintenances(
        self,
        asset_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        maintenance_type: str | None = None
    ) -> List[Maintenance]:
        """
        Filtra o histórico global ou individual de manutenções por período e tipo 
        (Preventiva ou Corretiva).
        """
        q = self.db.query(Maintenance)
        
        if asset_id is not None:
            q = q.filter(Maintenance.patrimonio_id == asset_id)
            
        if start_date is not None:
            q = q.filter(Maintenance.data_manutencao >= start_date)
            
        if end_date is not None:
            q = q.filter(Maintenance.data_manutencao <= end_date)
            
        if maintenance_type:
            q = q.filter(Maintenance.tipo == maintenance_type)
            
        return q.order_by(Maintenance.data_manutencao.desc()).all()
