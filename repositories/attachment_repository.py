from typing import List
from sqlalchemy.orm import Session
from models.attachment import Attachment
from repositories.base_repository import BaseRepository

class AttachmentRepository(BaseRepository[Attachment]):
    def __init__(self, db: Session):
        super().__init__(Attachment, db)

    def get_by_asset_id(self, asset_id: int) -> List[Attachment]:
        """Busca anexos vinculados diretamente a um patrimônio."""
        return (
            self.db.query(Attachment)
            .filter(Attachment.patrimonio_id == asset_id)
            .all()
        )

    def get_by_maintenance_id(self, maintenance_id: int) -> List[Attachment]:
        """Busca anexos vinculados a um registro específico de manutenção."""
        return (
            self.db.query(Attachment)
            .filter(Attachment.manutencao_id == maintenance_id)
            .all()
        )
