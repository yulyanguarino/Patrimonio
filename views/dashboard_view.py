import flet as ft
from views.base_view import BaseView
from controllers.dashboard_controller import DashboardController
from components.stat_card import StatCard

class DashboardView(BaseView):
    def __init__(self, page: ft.Page, db, navigate_to, **kwargs):
        super().__init__(page, **kwargs)
        self.db = db
        self.navigate_to = navigate_to
        self.controller = DashboardController(db)
        
        self.title_text = ft.Text("Dashboard Geral", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
        self.subtitle_text = ft.Text("Indicadores em tempo real e distribuição física dos bens patrimoniais.", color=ft.Colors.ON_SURFACE_VARIANT, size=14)
        
        # Cards de Estatística
        self.card_total = StatCard("TOTAL DE BENS", "0", ft.Icons.INVENTORY_ROUNDED, ft.Colors.BLUE_400)
        self.card_available = StatCard("DISPONÍVEIS", "0", ft.Icons.CHECK_CIRCLE_ROUNDED, ft.Colors.GREEN_400)
        self.card_in_use = StatCard("EM USO", "0", ft.Icons.PEOPLE_ROUNDED, ft.Colors.BLUE_200)
        self.card_maintenance = StatCard("EM MANUTENÇÃO", "0", ft.Icons.BUILD_ROUNDED, ft.Colors.AMBER_400)
        self.card_retired = StatCard("BAIXADOS", "0", ft.Icons.CANCEL_ROUNDED, ft.Colors.RED_400)
        
        self.cards_row = ft.Row([
            self.card_total,
            self.card_available,
            self.card_in_use,
            self.card_maintenance,
            self.card_retired
        ], spacing=15, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Distribuições de dados (Listas com barras de progresso)
        self.sectors_col = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        self.categories_col = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        
        self.distribution_row = ft.Row([
            # Setores Card
            ft.Container(
                content=ft.Column([
                    ft.Text("Distribuição por Setor", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    self.sectors_col
                ], expand=True),
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=12,
                padding=20,
                expand=True
            ),
            # Categorias Card
            ft.Container(
                content=ft.Column([
                    ft.Text("Distribuição por Categoria", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    self.categories_col
                ], expand=True),
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=12,
                padding=20,
                expand=True
            )
        ], spacing=20, expand=True)
        
        self.content = ft.Column([
            self.title_text,
            self.subtitle_text,
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            self.cards_row,
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            self.distribution_row
        ], expand=True, spacing=10)

    def on_mount(self) -> None:
        self.refresh_dashboard()

    def refresh_dashboard(self):
        metrics = self.controller.get_metrics()
        
        # Atualiza os valores textuais dos cards
        self.card_total.update_value(str(metrics["Total"]))
        self.card_available.update_value(str(metrics["Disponível"]))
        self.card_in_use.update_value(str(metrics["Em uso"]))
        self.card_maintenance.update_value(str(metrics["Em manutenção"]))
        self.card_retired.update_value(str(metrics["Baixado"]))
        
        total_assets = max(metrics["Total"], 1)
        
        # Carrega a distribuição por setor
        sectors_data = self.controller.get_sector_distribution()
        self.sectors_col.controls.clear()
        if not sectors_data:
            self.sectors_col.controls.append(
                ft.Text("Nenhum patrimônio alocado em setores.", italic=True, size=13, color=ft.Colors.ON_SURFACE_VARIANT)
            )
        else:
            for sector_name, count in sectors_data:
                percentage = count / total_assets
                self.sectors_col.controls.append(
                    self._build_distribution_row(sector_name, count, percentage, ft.Colors.BLUE_400)
                )
        try:
            self.sectors_col.update()
        except RuntimeError:
            pass
        
        # Carrega a distribuição por categoria
        categories_data = self.controller.get_category_distribution()
        self.categories_col.controls.clear()
        if not categories_data:
            self.categories_col.controls.append(
                ft.Text("Nenhum patrimônio alocado em categorias.", italic=True, size=13, color=ft.Colors.ON_SURFACE_VARIANT)
            )
        else:
            for category_name, count in categories_data:
                percentage = count / total_assets
                self.categories_col.controls.append(
                    self._build_distribution_row(category_name, count, percentage, ft.Colors.GREEN_400)
                )
        try:
            self.categories_col.update()
        except RuntimeError:
            pass

    def _build_distribution_row(self, name: str, count: int, percentage: float, bar_color: str):
        return ft.Column([
            ft.Row([
                ft.Text(name, size=13, weight=ft.FontWeight.W_500),
                ft.Text(f"{count} ({percentage * 100:.1f}%)", size=13, weight=ft.FontWeight.BOLD, color=bar_color)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.ProgressBar(
                value=percentage,
                color=bar_color,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                height=8,
                border_radius=4
            )
        ], spacing=5)
