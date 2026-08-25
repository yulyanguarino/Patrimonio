import flet as ft
from config.database import SessionLocal
from components.sidebar import Sidebar
from web.status_server import start_server, stop_server

# Importação das Views
from views.dashboard_view import DashboardView
from views.sector_view import SectorView
from views.category_view import CategoryView
from views.employee_view import EmployeeView
from views.asset_list_view import AssetListView
from views.asset_detail_view import AssetDetailView
from views.maintenance_view import MaintenanceView

class PatrimonioApp(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._custom_page = page
        self.expand = True
        self.spacing = 0
        
        # Cria uma conexão de banco dedicada à sessão do aplicativo/sessão
        self.db = SessionLocal()

        # Sobe o servidor local de status (usado pelo QR Code no modo desktop).
        # Quando hospedado (web), a página de status é servida via rota pública
        # em web_main.py -- não precisa desse servidor local.
        if not page.web:
            start_server()
        
        # Contêiner onde a tela ativa será renderizada
        self.main_content = ft.Container(
            expand=True,
            bgcolor="#121212",
        )
        self.current_route = "/dashboard"
        
        # Dicionário de rotas -> Views correspondentes
        self.views_map = {
            "/dashboard": DashboardView,
            "/sectors": SectorView,
            "/categories": CategoryView,
            "/employees": EmployeeView,
            "/assets": AssetListView,
            "/asset-detail": AssetDetailView,
            "/maintenances": MaintenanceView,
        }
        
        # Inicializa a Sidebar de navegação
        self.sidebar = Sidebar(self.page, self.current_route, self.navigate_to)
        
        self.controls = [
            self.sidebar,
            self.main_content
        ]
        
    def did_mount(self):
        self.navigate_to("/dashboard")

    @property
    def page(self):
        return self._custom_page

    def navigate_to(self, route: str, **kwargs) -> None:
        """
        Navega para a rota especificada, recriando a view correspondente
        e passando parâmetros arbitrários (como IDs para telas de detalhe).
        """
        view_class = self.views_map.get(route)
        if not view_class:
            return
            
        # Atualiza o item ativo na barra lateral
        self.current_route = route
        self.sidebar.active_route = route
        self.sidebar.content = self.sidebar._build_content()
        try:
            self.sidebar.update()
        except RuntimeError:
            pass
        
        # Instancia a nova tela
        view = view_class(self.page, db=self.db, navigate_to=self.navigate_to, **kwargs)
        self.main_content.content = view
        try:
            self.main_content.update()
        except RuntimeError:
            pass
        
        # Executa o ciclo de vida de montagem da tela (carregamento de dados)
        view.on_mount()

    def close(self) -> None:
        """Libera os recursos do banco de dados e do servidor local ao fechar a janela/sessão."""
        if not self.page.web:
            stop_server()
        self.db.close()
