import flet as ft
from views.base_view import BaseView
from controllers.category_controller import CategoryController
from components.custom_table import CustomTable
from components.dialogs import show_success_snackbar, show_error_snackbar, show_confirm_dialog

class CategoryView(BaseView):
    def __init__(self, page: ft.Page, db, navigate_to, **kwargs):
        super().__init__(page, **kwargs)
        self.db = db
        self.navigate_to = navigate_to
        self.controller = CategoryController(db)
        self.editing_id = None  # None = cadastrando nova, id = editando existente

        # Elementos da UI
        self.title_text = ft.Text("Cadastro de Categorias", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
        self.name_field = ft.TextField(
            label="Nome da Categoria",
            expand=True,
            on_submit=self._save_category,
            border_radius=8
        )
        self.save_btn = ft.ElevatedButton(
            "Adicionar",
            icon=ft.Icons.ADD_ROUNDED,
            on_click=self._save_category,
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
            self.save_btn,
            self.cancel_edit_btn
        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # Tabela Customizada
        self.table = CustomTable(
            columns=["ID", "Nome da Categoria", "Ações"],
            row_builder_func=self._build_row,
            rows_per_page=10
        )

        self.content = ft.Column([
            self.title_text,
            ft.Text("Gerencie as categorias de patrimônios cadastradas no sistema (ex: Notebook, Mesa, Cadeira).", color=ft.Colors.ON_SURFACE_VARIANT, size=14),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            self.form_row,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            self.table
        ], expand=True, spacing=10)

    def on_mount(self) -> None:
        self.refresh_table()

    def refresh_table(self):
        categories = self.controller.list_categories()
        self.table.update_data(categories)

    def _build_row(self, category):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(category.id))),
                ft.DataCell(ft.Text(category.nome, weight=ft.FontWeight.W_500)),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            ft.Icons.EDIT_ROUNDED,
                            tooltip="Editar Categoria",
                            on_click=lambda e: self._edit_category(category)
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE_ROUNDED,
                            icon_color=ft.Colors.RED_400,
                            tooltip="Excluir Categoria",
                            on_click=lambda e: self._delete_confirm(category.id, category.nome)
                        )
                    ])
                )
            ]
        )

    def _edit_category(self, category):
        self.editing_id = category.id
        self.name_field.value = category.nome
        self.save_btn.text = "Atualizar"
        self.save_btn.icon = ft.Icons.SAVE_ROUNDED
        self.cancel_edit_btn.visible = True
        try:
            self.name_field.update()
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
        try:
            self.name_field.update()
            self.save_btn.update()
            self.cancel_edit_btn.update()
        except RuntimeError:
            pass

    def _save_category(self, e):
        name = self.name_field.value.strip()
        if not name:
            show_error_snackbar(self.page, "O nome da categoria é obrigatório.")
            return

        if self.editing_id is None:
            success, res = self.controller.create_category(name)
            success_message = f"Categoria '{res.nome}' cadastrada com sucesso!" if success else res
        else:
            success, res = self.controller.update_category(self.editing_id, name)
            success_message = f"Categoria '{res.nome}' atualizada com sucesso!" if success else res

        if success:
            show_success_snackbar(self.page, success_message)
            self._cancel_edit(None)
            self.refresh_table()
        else:
            show_error_snackbar(self.page, res)

    def _delete_confirm(self, category_id: int, category_name: str):
        show_confirm_dialog(
            self.page,
            "Confirmar Exclusão",
            f"Deseja realmente excluir a categoria '{category_name}'?",
            lambda: self._delete_category(category_id)
        )

    def _delete_category(self, category_id: int):
        success, message = self.controller.delete_category(category_id)
        if success:
            if self.editing_id == category_id:
                self._cancel_edit(None)
            show_success_snackbar(self.page, message)
            self.refresh_table()
        else:
            show_error_snackbar(self.page, message)
