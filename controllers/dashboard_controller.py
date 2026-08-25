from controllers.base_controller import BaseController
from services.asset_service import AssetService

class DashboardController(BaseController):
    def __init__(self, db):
        super().__init__(db)
        self.service = AssetService(db)

    def get_metrics(self):
        """Retorna o dicionário de métricas de contagem (Total, Disponível, Em uso, etc.)."""
        try:
            return self.service.get_dashboard_metrics()
        except Exception:
            return {"Total": 0, "Disponível": 0, "Em uso": 0, "Em manutenção": 0, "Baixado": 0}

    def get_sector_distribution(self):
        """Retorna o resumo numérico de patrimônios por setor."""
        try:
            return self.service.get_assets_by_sector_summary()
        except Exception:
            return []

    def get_category_distribution(self):
        """Retorna o resumo numérico de patrimônios por categoria."""
        try:
            return self.service.get_assets_by_category_summary()
        except Exception:
            return []
