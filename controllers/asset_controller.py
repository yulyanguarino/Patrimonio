from datetime import date
from controllers.base_controller import BaseController
from services.asset_service import AssetService
from services.attachment_service import AttachmentService
from services.label_service import LabelService
from utils.exceptions import BusinessRuleException

class AssetController(BaseController):
    def __init__(self, db):
        super().__init__(db)
        self.service = AssetService(db)
        self.attachment_service = AttachmentService(db)
        self.label_service = LabelService(db)

    def search_assets(self, query_text: str | None = None, category_id: int | None = None, sector_id: int | None = None, status: str | None = None):
        """Retorna lista filtrada de patrimônios."""
        try:
            return self.service.search_assets(
                query_text=query_text,
                category_id=category_id,
                sector_id=sector_id,
                status=status
            )
        except Exception:
            return []

    def get_asset(self, asset_id: int):
        """Busca um patrimônio pelo ID."""
        try:
            return self.service.get_asset_by_id(asset_id)
        except Exception:
            return None

    def create_asset(
        self,
        nome: str,
        categoria_id: int,
        setor_id: int,
        funcionario_id: int | None = None,
        data_compra: date | None = None,
        nota_fiscal: str | None = None,
        garantia_meses: int | None = None,
        status: str = "Disponível",
        observacoes: str | None = None
    ):
        """Tenta criar um patrimônio aplicando as regras de negócio de status e número."""
        try:
            asset = self.service.create_asset(
                nome=nome,
                categoria_id=categoria_id,
                setor_id=setor_id,
                funcionario_id=funcionario_id,
                data_compra=data_compra,
                nota_fiscal=nota_fiscal,
                garantia_meses=garantia_meses,
                status=status,
                observacoes=observacoes
            )
            return True, asset
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    def update_asset(
        self,
        asset_id: int,
        nome: str,
        categoria_id: int,
        setor_id: int,
        funcionario_id: int | None = None,
        data_compra: date | None = None,
        nota_fiscal: str | None = None,
        garantia_meses: int | None = None,
        status: str = "Disponível",
        observacoes: str | None = None
    ):
        """Tenta atualizar os dados de um patrimônio (apenas se não estiver Baixado)."""
        try:
            asset = self.service.update_asset(
                asset_id=asset_id,
                nome=nome,
                categoria_id=categoria_id,
                setor_id=setor_id,
                funcionario_id=funcionario_id,
                data_compra=data_compra,
                nota_fiscal=nota_fiscal,
                garantia_meses=garantia_meses,
                status=status,
                observacoes=observacoes
            )
            return True, asset
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    def delete_asset(self, asset_id: int):
        """Remove fisicamente o patrimônio e limpa arquivos anexos do disco."""
        try:
            self.service.delete_asset(asset_id)
            return True, "Patrimônio excluído com sucesso."
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    def add_attachment(self, source_path: str, tipo_documento: str, asset_id: int):
        """Adiciona anexo associado a um patrimônio."""
        try:
            attachment = self.attachment_service.add_attachment(
                source_path=source_path,
                tipo_documento=tipo_documento,
                patrimonio_id=asset_id
            )
            return True, attachment
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    def delete_attachment(self, attachment_id: int):
        """Remove o anexo física e logicamente."""
        try:
            self.attachment_service.delete_attachment(attachment_id)
            return True, "Anexo excluído com sucesso."
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    def generate_label(self, asset_id: int):
        """Gera o PDF de etiqueta (QR Code + número patrimonial) para impressão térmica."""
        try:
            path = self.label_service.generate_label(asset_id)
            return True, path
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado ao gerar etiqueta: {str(e)}"

    def generate_labels_bulk(self, asset_ids: list[int]):
        """Gera um único PDF com uma etiqueta por página, para vários patrimônios de uma vez."""
        try:
            path = self.label_service.generate_labels_bulk(asset_ids)
            return True, path
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado ao gerar etiquetas: {str(e)}"
