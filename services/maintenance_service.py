from datetime import date
from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session
from models.maintenance import Maintenance
from repositories.maintenance_repository import MaintenanceRepository
from repositories.asset_repository import AssetRepository
from utils.exceptions import BusinessRuleException

class MaintenanceService:
    def __init__(self, db: Session):
        self.db = db
        self.maintenance_repo = MaintenanceRepository(db)
        self.asset_repo = AssetRepository(db)

    def register_maintenance(
        self,
        patrimonio_id: int,
        tipo: str,
        data_manutencao: date,
        prestador: str,
        descricao_problema: str,
        servico_executado: str,
        valor_gasto: float | Decimal,
        data_proxima: date | None = None,
        observacoes: str | None = None,
        set_asset_in_maintenance: bool = False
    ) -> Maintenance:
        """
        Registra uma nova manutenção preventiva ou corretiva com todas as regras 
        de negócio e validações monetárias aplicadas.
        """
        asset = self.asset_repo.get_by_id(patrimonio_id)
        if not asset:
            raise BusinessRuleException("Patrimônio não encontrado.")
            
        # Bloqueia registros de manutenção para bens já retirados (baixados)
        if asset.status == "Baixado":
            raise BusinessRuleException("Não é possível registrar manutenções para um patrimônio baixado.")

        # Validações dos campos obrigatórios
        if tipo not in ("Preventiva", "Corretiva"):
            raise BusinessRuleException("O tipo de manutenção deve ser 'Preventiva' ou 'Corretiva'.")
            
        if not prestador.strip():
            raise BusinessRuleException("O prestador do serviço ou técnico é obrigatório.")
            
        if not descricao_problema.strip():
            raise BusinessRuleException("A descrição do problema é obrigatória.")
            
        if not servico_executado.strip():
            raise BusinessRuleException("O serviço executado é obrigatório.")
            
        # Validação financeira
        try:
            valor_dec = Decimal(str(valor_gasto))
        except ValueError:
            raise BusinessRuleException("O valor gasto informado é inválido.")
            
        if valor_dec < Decimal("0.00"):
            raise BusinessRuleException("O valor gasto não pode ser negativo.")
            
        # Validação temporal
        if data_proxima and data_proxima < data_manutencao:
            raise BusinessRuleException("A data da próxima manutenção não pode ser anterior à data atual.")

        # Cria a manutenção
        maint = Maintenance(
            patrimonio_id=patrimonio_id,
            tipo=tipo,
            data_manutencao=data_manutencao,
            prestador=prestador.strip(),
            descricao_problema=descricao_problema.strip(),
            servico_executado=servico_executado.strip(),
            valor_gasto=valor_dec,
            data_proxima=data_proxima,
            observacoes=observacoes.strip() if observacoes else None
        )
        
        # Modifica status do patrimônio se solicitado pelo fluxo visual (operação Corretiva)
        if set_asset_in_maintenance and asset.status != "Em manutenção":
            asset.status = "Em manutenção"
            asset.funcionario_id = None  # Remove responsável ao enviar para reparo
            self.asset_repo.update(asset)
            
        return self.maintenance_repo.create(maint)

    def get_maintenances_by_asset_id(self, asset_id: int) -> List[Maintenance]:
        """Consulta histórico de manutenções de um determinado bem."""
        return self.maintenance_repo.get_by_asset_id(asset_id)

    def filter_maintenances(
        self,
        asset_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        maintenance_type: str | None = None
    ) -> List[Maintenance]:
        """Filtra manutenções globais ou individuais por critérios de data e tipo."""
        return self.maintenance_repo.filter_maintenances(
            asset_id=asset_id,
            start_date=start_date,
            end_date=end_date,
            maintenance_type=maintenance_type
        )
