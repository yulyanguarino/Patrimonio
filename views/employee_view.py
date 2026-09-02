import flet as ft
from views.base_view import BaseView
from controllers.employee_controller import EmployeeController
from controllers.sector_controller import SectorController
from components.custom_table import CustomTable
from components.dialogs import show_success_snackbar, show_error_snackbar, show_confirm_dialog

class EmployeeView(BaseView):
    def __init__(self, page: ft.Page, db, navigate_to, **kwargs):
        super().__init__(page, **kwargs)
        self.db = db
        self.navigate_to = navigate_to
        self.controller = EmployeeController(db)
        self.sector_controller = SectorController(db)
        self.editing_id = None  # None = cadastrando novo, id = editando existente

        # Elementos da UI
        self.title_text = ft.Text("Cadastro de Funcionários", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
        self.name_field = ft.TextField(
            label="Nome do Funcionário",
            expand=True,
            border_radius=8
        )
        self.sector_dropdown = ft.Dropdown(
            label="Setor",
            width=250,
            options=[],
            enable_filter=True,
            editable=True,
            border_radius=8
        )
        self.save_btn = ft.ElevatedButton(
            "Adicionar",
            icon=ft.Icons.ADD_ROUNDED,
            on_click=self._save_employee,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.BLUE_900,
                color=ft.Colors.BLUE_100
            )
        )
        self.cancel_edit_btn = ft.TextButton(
            "Cancelar edição",
            on_click=self._cancel_edit,
            visible=False
        )

        # Form Row
        self.form_row = ft.Row([
            self.name_field,
            self.sector_dropdown,
            self.save_btn,
            self.cancel_edit_btn
        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # Tabela Customizada
        self.table = CustomTable(
            columns=["ID", "Nome do Funcionário", "Setor", "Ações"],
            row_builder_func=self._build_row,
            rows_per_page=10
        )

        self.content = ft.Column([
            self.title_text,
            ft.Text("Gerencie os funcionários da empresa para alocação e controle de responsabilidade sobre os patrimônios.", color=ft.Colors.ON_SURFACE_VARIANT, size=14),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            self.form_row,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            self.table
        ], expand=True, spacing=10)

    def on_mount(self) -> None:
        self.refresh_dropdown()
        self.refresh_table()

    def refresh_dropdown(self):
        sectors = self.sector_controller.list_sectors()
        self.sector_dropdown.options = [
            ft.dropdown.Option(key=str(s.id), text=s.nome) for s in sectors
        ]
        if self.editing_id is None:
            self.sector_dropdown.value = str(sectors[0].id) if sectors else None
        try:
            self.sector_dropdown.update()
        except RuntimeError:
            pass

    def refresh_table(self):
        employees = self.controller.list_employees()
        self.table.update_data(employees)

    def _build_row(self, employee):
        sector_name = employee.sector.nome if employee.sector else "Sem Setor"
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(employee.id))),
                ft.DataCell(ft.Text(employee.nome, weight=ft.FontWeight.W_500)),
                ft.DataCell(ft.Text(sector_name)),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            ft.Icons.EDIT_ROUNDED,
                            tooltip="Editar Funcionário",
                            on_click=lambda e: self._edit_employee(employee)
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE_ROUNDED,
                            icon_color=ft.Colors.RED_400,
                            tooltip="Excluir Funcionário",
                            on_click=lambda e: self._delete_confirm(employee.id, employee.nome)
                        )
                    ])
                )
            ]
        )

    def _edit_employee(self, employee):
        self.editing_id = employee.id
        self.name_field.value = employee.nome
        self.sector_dropdown.value = str(employee.setor_id) if employee.setor_id else None
        self.save_btn.text = "Atualizar"
        self.save_btn.icon = ft.Icons.SAVE_ROUNDED
        self.cancel_edit_btn.visible = True
        try:
            self.name_field.update()
            self.sector_dropdown.update()
            self.save_btn.update()
            self.cancel_edit_btn.update()
            self.name_field.focus()
        except RuntimeError:
            pass

    def _cancel_edit(self, e):
        self.editing_id = None
        self.name_field.value = ""
        self.save_btn.text = "Adicionar"
        self.save_btn.icon = ft.Icons.ADD_ROUNDED
        self.cancel_edit_btn.visible = False
        self.refresh_dropdown()
        try:
            self.name_field.update()
            self.save_btn.update()
            self.cancel_edit_btn.update()
        except RuntimeError:
            pass

    def _save_employee(self, e):
        name = self.name_field.value.strip()
        sector_id_str = self.sector_dropdown.value

        if not name:
            show_error_snackbar(self.page, "O nome do funcionário é obrigatório.")
            return
        if not sector_id_str:
            show_error_snackbar(self.page, "É necessário selecionar um setor válido. Se necessário, cadastre um setor primeiro.")
            return

        if self.editing_id is None:
            success, res = self.controller.create_employee(name, int(sector_id_str))
            success_message = f"Funcionário '{res.nome}' cadastrado com sucesso!" if success else res
        else:
            success, res = self.controller.update_employee(self.editing_id, name, int(sector_id_str))
            success_message = f"Funcionário '{res.nome}' atualizado com sucesso!" if success else res

        if success:
            show_success_snackbar(self.page, success_message)
            self._cancel_edit(None)
            self.refresh_table()
        else:
            show_error_snackbar(self.page, res)

    def _delete_confirm(self, employee_id: int, employee_name: str):
        show_confirm_dialog(
            self.page,
            "Confirmar Exclusão",
            f"Deseja realmente excluir o funcionário '{employee_name}'?",
            lambda: self._delete_employee(employee_id)
        )

    def _delete_employee(self, employee_id: int):
        success, message = self.controller.delete_employee(employee_id)
        if success:
            if self.editing_id == employee_id:
                self._cancel_edit(None)
            show_success_snackbar(self.page, message)
            self.refresh_table()
        else:
            show_error_snackbar(self.page, message)
