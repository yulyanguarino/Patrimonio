import flet as ft
from views.base_view import BaseView
from controllers.sector_controller import SectorController
from components.custom_table import CustomTable
from components.dialogs import show_success_snackbar, show_error_snackbar, show_confirm_dialog

class SectorView(BaseView):
    def __init__(self, page: ft.Page, db, navigate_to, **kwargs):
        super().__init__(page, **kwargs)
        self.db = db
        self.navigate_to = navigate_to
        self.controller = SectorController(db)
        
        # Elementos da UI
        self.title_text = ft.Text("Cadastro de Setores", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
        self.name_field = ft.TextField(
            label="Nome do Setor", 
            expand=True,
            on_submit=self._add_sector,
            border_radius=8
        )
        self.add_btn = ft.ElevatedButton(
            "Adicionar", 
            icon=ft.Icons.ADD_ROUNDED, 
            on_click=self._add_sector,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.BLUE_900,
                color=ft.Colors.BLUE_100
            )
        )
        
        # Form Row
        self.form_row = ft.Row([
            self.name_field,
            self.add_btn
        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Tabela Customizada
        self.table = CustomTable(
            columns=["ID", "Nome do Setor", "Ações"],
            row_builder_func=self._build_row,
            rows_per_page=10
        )
        
        self.content = ft.Column([
            self.title_text,
            ft.Text("Gerencie os setores internos da empresa que possuem patrimônios e funcionários associados.", color=ft.Colors.ON_SURFACE_VARIANT, size=14),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            self.form_row,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            self.table
        ], expand=True, spacing=10)

    def on_mount(self) -> None:
        self.refresh_table()

    def refresh_table(self):
        sectors = self.controller.list_sectors()
        self.table.update_data(sectors)

    def _build_row(self, sector):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(sector.id))),
                ft.DataCell(ft.Text(sector.nome, weight=ft.FontWeight.W_500)),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE_ROUNDED,
                            icon_color=ft.Colors.RED_400,
                            tooltip="Excluir Setor",
                            on_click=lambda e: self._delete_confirm(sector.id, sector.nome)
                        )
                    ])
                )
            ]
        )

    def _add_sector(self, e):
        name = self.name_field.value.strip()
        if not name:
            show_error_snackbar(self.page, "O nome do setor é obrigatório.")
            return
            
        success, res = self.controller.create_sector(name)
        if success:
            show_success_snackbar(self.page, f"Setor '{res.nome}' cadastrado com sucesso!")
            self.name_field.value = ""
            try:
                self.name_field.update()
            except RuntimeError:
                pass
            self.refresh_table()
        else:
            show_error_snackbar(self.page, res)

    def _delete_confirm(self, sector_id: int, sector_name: str):
        show_confirm_dialog(
            self.page,
            "Confirmar Exclusão",
            f"Deseja realmente excluir o setor '{sector_name}'?",
            lambda: self._delete_sector(sector_id)
        )

    def _delete_sector(self, sector_id: int):
        success, message = self.controller.delete_sector(sector_id)
        if success:
            show_success_snackbar(self.page, message)
            self.refresh_table()
        else:
            show_error_snackbar(self.page, message)
