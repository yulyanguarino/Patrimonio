import os
import shutil
import uuid
from pathlib import Path
from typing import List
from sqlalchemy.orm import Session
from models.attachment import Attachment
from repositories.attachment_repository import AttachmentRepository
from repositories.asset_repository import AssetRepository
from repositories.maintenance_repository import MaintenanceRepository
from config.settings import ATTACHMENTS_DIR
from utils.exceptions import BusinessRuleException

class AttachmentService:
    def __init__(self, db: Session):
        self.db = db
        self.attachment_repo = AttachmentRepository(db)
        self.asset_repo = AssetRepository(db)
        self.maintenance_repo = MaintenanceRepository(db)

    def add_attachment(
        self,
        source_path: str,
        tipo_documento: str,
        patrimonio_id: int | None = None,
        manutencao_id: int | None = None
    ) -> Attachment:
        """
        Copia um arquivo físico para a pasta de armazenamento interno do sistema,
        renomeando-o com UUID v4 para evitar colisões e grava o registro no banco de dados.
        """
        # Garante vínculo de destino
        if not patrimonio_id and not manutencao_id:
            raise BusinessRuleException("O anexo deve estar vinculado a um patrimônio ou a uma manutenção.")

        if patrimonio_id and not self.asset_repo.get_by_id(patrimonio_id):
            raise BusinessRuleException("O patrimônio associado ao anexo é inválido ou não existe.")

        if manutencao_id and not self.maintenance_repo.get_by_id(manutencao_id):
            raise BusinessRuleException("A manutenção associada ao anexo é inválida ou não existe.")

        # Verifica arquivo de origem
        src_file = Path(source_path)
        if not src_file.exists() or not src_file.is_file():
            raise BusinessRuleException(f"O arquivo físico de origem '{source_path}' não foi localizado.")

        # Validação do tipo de documento
        valid_types = {"Foto", "Nota Fiscal", "Manual", "Garantia", "Outros"}
        if tipo_documento not in valid_types:
            raise BusinessRuleException(f"Tipo de documento '{tipo_documento}' é inválido.")

        # Garante diretório de destino
        ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)

        # Gera nome único UUID preservando a extensão original
        file_ext = src_file.suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        destination_path = ATTACHMENTS_DIR / unique_filename

        try:
            # Copia fisicamente o arquivo preservando permissões e datas
            shutil.copy2(src_file, destination_path)
        except Exception as e:
            raise BusinessRuleException(f"Falha ao transferir o arquivo físico para a pasta de anexos: {e}")

        # Grava registro no banco
        attachment = Attachment(
            patrimonio_id=patrimonio_id,
            manutencao_id=manutencao_id,
            nome_arquivo=src_file.name,
            caminho_local=str(destination_path),  # Caminho absoluto para fácil abertura no S.O.
            tipo_documento=tipo_documento
        )
        
        return self.attachment_repo.create(attachment)

    def delete_attachment(self, attachment_id: int) -> None:
        """Exclui o registro de anexo do banco de dados e remove o arquivo correspondente do disco."""
        attachment = self.attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise BusinessRuleException("Registro de anexo não localizado.")

        # Remove o arquivo físico do disco
        physical_path = Path(attachment.caminho_local)
        if physical_path.exists():
            try:
                os.remove(physical_path)
            except Exception as e:
                # Loga o erro, mas não interrompe a exclusão lógica se o arquivo físico foi corrompido/bloqueado
                print(f"[Warning] Falha ao excluir arquivo do disco: {physical_path}. Erro: {e}")

        self.attachment_repo.delete(attachment)

    def get_attachments_by_asset(self, asset_id: int) -> List[Attachment]:
        """Busca anexos vinculados a um patrimônio."""
        return self.attachment_repo.get_by_asset_id(asset_id)

    def get_attachments_by_maintenance(self, maintenance_id: int) -> List[Attachment]:
        """Busca anexos vinculados a uma manutenção."""
        return self.attachment_repo.get_by_maintenance_id(maintenance_id)
