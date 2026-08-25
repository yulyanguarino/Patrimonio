from datetime import date
from decimal import Decimal
from controllers.base_controller import BaseController
from services.maintenance_service import MaintenanceService
from services.attachment_service import AttachmentService
from utils.exceptions import BusinessRuleException

class MaintenanceController(BaseController):
    def __init__(self, db):
        super().__init__(db)
        self.service = MaintenanceService(db)
        self.attachment_service = AttachmentService(db)

    def list_maintenances(self, asset_id: int | None = None, start_date: date | None = None, end_date: date | None = None, maintenance_type: str | None = None):
        """Retorna histórico filtrado de manutenções."""
        try:
            return self.service.filter_maintenances(
                asset_id=asset_id,
                start_date=start_date,
                end_date=end_date,
                maintenance_type=maintenance_type
            )
        except Exception:
            return []

    def register_maintenance(
        self,
        patrimonio_id: int,
        tipo: str,
        data_manutencao: date,
        prestador: str,
        descricao_problema: str,
        servico_executado: str,
        valor_gasto: float,
        data_proxima: date | None = None,
        observacoes: str | None = None,
        set_asset_in_maintenance: bool = False
    ):
        """Registra uma nova manutenção e atualiza opcionalmente o status do patrimônio."""
        try:
            maint = self.service.register_maintenance(
                patrimonio_id=patrimonio_id,
                tipo=tipo,
                data_manutencao=data_manutencao,
                prestador=prestador,
                descricao_problema=descricao_problema,
                servico_executado=servico_executado,
                valor_gasto=valor_gasto,
                data_proxima=data_proxima,
                observacoes=observacoes,
                set_asset_in_maintenance=set_asset_in_maintenance
            )
            return True, maint
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    def add_maintenance_attachment(self, source_path: str, tipo_documento: str, manutencao_id: int):
        """Adiciona anexo físico/lógico associado a uma manutenção."""
        try:
            attachment = self.attachment_service.add_attachment(
                source_path=source_path,
                tipo_documento=tipo_documento,
                manutencao_id=manutencao_id
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

    def conclude_maintenance(self, asset_id: int):
        """Finaliza o ciclo de manutenção do patrimônio, retornando seu status para 'Disponível'."""
        try:
            asset = self.service.asset_repo.get_by_id(asset_id)
            if not asset:
                raise BusinessRuleException("Patrimônio não encontrado.")
            if asset.status != "Em manutenção":
                raise BusinessRuleException("O patrimônio não está com o status 'Em manutenção'.")
            asset.status = "Disponível"
            self.service.asset_repo.update(asset)
            return True, f"Manutenção concluída! O patrimônio [{asset.numero_patrimonial}] {asset.nome} retornou para o status 'Disponível'."
        except BusinessRuleException as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"
