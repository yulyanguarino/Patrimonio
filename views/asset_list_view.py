import flet as ft
import os
from datetime import datetime, date
from views.base_view import BaseView
from controllers.asset_controller import AssetController
from controllers.category_controller import CategoryController
from controllers.sector_controller import SectorController
from controllers.employee_controller import EmployeeController
from components.custom_table import CustomTable
from components.dialogs import show_success_snackbar, show_error_snackbar, show_confirm_dialog
from utils.uploads import resolve_picked_file
from utils.file_actions import reveal_file

class AssetListView(BaseView):
    def __init__(self, page: ft.Page, db, navigate_to, **kwargs):
        super().__init__(page, **kwargs)
        self.db = db
        self.navigate_to = navigate_to
        
        # Inicializa controladores
        self.controller = AssetController(db)
        self.category_controller = CategoryController(db)
        self.sector_controller = SectorController(db)
        self.employee_controller = EmployeeController(db)
        
        self.selected_date = None
        self.editing_asset = None  # None para Criar, Objeto Asset para Editar
        
        # DatePicker para Compra
        self.date_picker = ft.DatePicker(
            on_change=self._on_date_selected
        )
        if self.date_picker not in self.page.overlay:
            self.page.overlay.append(self.date_picker)
            
        # Elementos da UI
        self.title_text = ft.Text("Controle de Patrimônios", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
        
        # Filtros
        self.search_field = ft.TextField(
            label="Pesquisar por nome ou plaqueta",
            expand=True,
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            on_change=self._trigger_search,
            border_radius=8
        )
        
        self.filter_category = ft.Dropdown(
            label="Categoria",
            width=180,
            options=[],
            on_select=self._trigger_search,
            border_radius=8
        )
        
        self.filter_sector = ft.Dropdown(
            label="Setor",
            width=180,
            options=[],
            on_select=self._trigger_search,
            border_radius=8
        )
        
        self.filter_status = ft.Dropdown(
            label="Status",
            width=150,
            options=[
                ft.dropdown.Option("", "Todos"),
                ft.dropdown.Option("Disponível"),
                ft.dropdown.Option("Em uso"),
                ft.dropdown.Option("Em manutenção"),
                ft.dropdown.Option("Baixado"),
            ],
            value="",
            on_select=self._trigger_search,
            border_radius=8
        )
        
        self.new_asset_btn = ft.ElevatedButton(
            "Novo Patrimônio",
            icon=ft.Icons.ADD_ROUNDED,
            on_click=self._open_create_dialog,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.BLUE_400,
                color=ft.Colors.WHITE
            )
        )
        
        self.filter_row = ft.Row([
            self.search_field,
            self.filter_category,
            self.filter_sector,
            self.filter_status,
            self.new_asset_btn
        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Tabela
        self.table = CustomTable(
            columns=["Plaqueta", "Nome do Bem", "Categoria", "Setor", "Responsável", "Status", "Ações"],
            row_builder_func=self._build_row,
            rows_per_page=10
        )
        
        self.content = ft.Column([
            ft.Row([
                ft.Column([
                    self.title_text,
                    ft.Text("Consulte, edite, realize buscas e verifique a disponibilidade dos bens patrimoniais ativos.", color=ft.Colors.ON_SURFACE_VARIANT, size=14),
                ], expand=True),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            self.filter_row,
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            self.table
        ], expand=True, spacing=10)
        
        # Campos do Formulário Modal (Criar/Editar)
        self.form_nome = ft.TextField(label="Nome do Patrimônio*", border_radius=8)
        self.form_category = ft.Dropdown(label="Categoria*", hint_text="Selecione a Categoria", border_radius=8, expand=True)
        self.form_sector = ft.Dropdown(label="Setor*", hint_text="Selecione o Setor", border_radius=8, expand=True)
        self.form_status = ft.Dropdown(
            label="Status*",
            options=[
                ft.dropdown.Option("Disponível"),
                ft.dropdown.Option("Em uso"),
                ft.dropdown.Option("Baixado"),
            ],
            value="Disponível",
            on_select=self._on_form_status_change,
            border_radius=8,
            expand=True
        )
        self.form_employee = ft.Dropdown(label="Funcionário Responsável*", hint_text="Selecione o Responsável", visible=False, border_radius=8, expand=True)
        self.form_nf = ft.TextField(label="Nota Fiscal", border_radius=8, expand=True)
        self.selected_nf_path = None
        # Service (não controle visual): se auto-registra, não vai no page.overlay.
        self.nf_file_picker = ft.FilePicker()
        self.nf_file_text = ft.Text("Nenhum arquivo anexado", size=12, italic=True, color=ft.Colors.ON_SURFACE_VARIANT)
        self.nf_upload_btn = ft.IconButton(
            ft.Icons.ATTACH_FILE_ROUNDED,
            tooltip="Anexar Nota Fiscal (PDF ou imagem, opcional)",
            on_click=self._on_pick_nf_file
        )
        self.form_garantia = ft.TextField(label="Garantia (Meses)", keyboard_type=ft.KeyboardType.NUMBER, border_radius=8)
        self.form_obs = ft.TextField(label="Observações", multiline=True, min_lines=2, max_lines=4, border_radius=8)
        
        self.date_btn = ft.OutlinedButton(
            "Selecionar Data de Compra",
            icon=ft.Icons.CALENDAR_MONTH_ROUNDED,
            on_click=self._open_date_picker
        )
        self.date_text = ft.Text("Nenhuma data selecionada", size=13, italic=True)

    def on_mount(self) -> None:
        self.load_dropdowns()
        self.refresh_table()

    def load_dropdowns(self):
        categories = self.category_controller.list_categories()
        sectors = self.sector_controller.list_sectors()
        employees = self.employee_controller.list_employees()
        
        # Popula os filtros de busca
        self.filter_category.options = [ft.dropdown.Option("", "Todas Categorias")] + [
            ft.dropdown.Option(str(c.id), c.nome) for c in categories
        ]
        self.filter_category.value = ""
        try:
            self.filter_category.update()
        except RuntimeError:
            pass
        
        self.filter_sector.options = [ft.dropdown.Option("", "Todos Setores")] + [
            ft.dropdown.Option(str(s.id), s.nome) for s in sectors
        ]
        self.filter_sector.value = ""
        try:
            self.filter_sector.update()
        except RuntimeError:
            pass
        
        # Popula campos do modal
        self.form_category.options = [ft.dropdown.Option(str(c.id), c.nome) for c in categories]
        self.form_sector.options = [ft.dropdown.Option(str(s.id), s.nome) for s in sectors]
        self.form_employee.options = [ft.dropdown.Option(str(e.id), e.nome) for e in employees]

    def refresh_table(self):
        raw_query = self.search_field.value.strip() if self.search_field.value else ""
        query = raw_query if raw_query else None
        
        cat_val = self.filter_category.value
        cat_id = int(cat_val) if (cat_val and cat_val != "") else None
        
        sec_val = self.filter_sector.value
        sec_id = int(sec_val) if (sec_val and sec_val != "") else None
        
        stat_val = self.filter_status.value
        status = stat_val if (stat_val and stat_val != "") else None
        
        assets = self.controller.search_assets(query, cat_id, sec_id, status)
        self.table.update_data(assets)

    def _trigger_search(self, e):
        self.refresh_table()

    def _open_date_picker(self, e):
        if self.date_picker not in self.page.overlay:
            self.page.overlay.append(self.date_picker)
        self.date_picker.open = True
        try:
            self.page.update()
        except RuntimeError:
            pass

    def _on_date_selected(self, e):
        if self.date_picker.value:
            self.selected_date = self.date_picker.value.date()
            self.date_text.value = self.selected_date.strftime("%d/%m/%Y")
            self.date_text.italic = False
            try:
                self.date_text.update()
            except RuntimeError:
                pass

    def _build_row(self, asset):
        # Traduz status para cores
        status_colors = {
            "Disponível": ft.Colors.GREEN_400,
            "Em uso": ft.Colors.BLUE_400,
            "Em manutenção": ft.Colors.AMBER_400,
            "Baixado": ft.Colors.RED_400
        }
        status_color = status_colors.get(asset.status, ft.Colors.ON_SURFACE)
        
        resp_name = asset.employee.nome if asset.employee else "-"
        
        # Desabilita botão de edição caso o status seja Baixado (terminalidade)
        is_baixado = asset.status == "Baixado"
        
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(asset.numero_patrimonial, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text(asset.nome, weight=ft.FontWeight.W_500)),
                ft.DataCell(ft.Text(asset.category.nome if asset.category else "-")),
                ft.DataCell(ft.Text(asset.sector.nome if asset.sector else "-")),
                ft.DataCell(ft.Text(resp_name)),
                ft.DataCell(ft.Container(
                    content=ft.Text(asset.status, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=status_color,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                    border_radius=4
                )),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            ft.Icons.INFO_OUTLINE_ROUNDED,
                            tooltip="Detalhes",
                            on_click=lambda e: self.navigate_to("/asset-detail", asset_id=asset.id)
                        ),
                        ft.IconButton(
                            ft.Icons.EDIT_ROUNDED,
                            tooltip="Editar" if not is_baixado else "Baixado (Somente Leitura)",
                            disabled=is_baixado,
                            on_click=lambda e: self._open_edit_dialog(asset)
                        ),
                        ft.IconButton(
                            ft.Icons.QR_CODE_2_ROUNDED,
                            tooltip="Gerar Etiqueta",
                            data=asset.id,
                            on_click=self._generate_label
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE_ROUNDED,
                            icon_color=ft.Colors.RED_400,
                            tooltip="Excluir Patrimônio (Erro de Cadastro)",
                            on_click=lambda e: self._delete_confirm(asset.id, asset.nome, asset.numero_patrimonial)
                        )
                    ], spacing=0)
                )
            ]
        )

    async def _on_pick_nf_file(self, e):
        files = await self.nf_file_picker.pick_files(
            allow_multiple=False,
            dialog_title="Selecione a Nota Fiscal (PDF ou imagem)"
        )
        if files:
            self.selected_nf_path = await resolve_picked_file(self.page, self.nf_file_picker, files[0])
            self.nf_file_text.value = files[0].name
            self.nf_file_text.italic = False
            self.nf_file_text.weight = ft.FontWeight.BOLD
            self.nf_file_text.color = ft.Colors.ON_SURFACE
            try:
                self.nf_file_text.update()
            except RuntimeError:
                pass

    def _on_form_status_change(self, e):
        self.form_employee.visible = (self.form_status.value == "Em uso")
        try:
            self.form_employee.update()
        except RuntimeError:
            pass

    def _open_create_dialog(self, e):
        self.editing_asset = None
        self.selected_date = None
        
        # Garante a atualização mais recente das opções de categoria, setor e funcionários
        self.load_dropdowns()
        
        # Define as 3 opções de status padrão
        self.form_status.options = [
            ft.dropdown.Option("Disponível"),
            ft.dropdown.Option("Em uso"),
            ft.dropdown.Option("Baixado"),
        ]
        
        # Limpa erros visuais de validação anteriores
        self.form_nome.error_text = None
        self.form_category.error_text = None
        self.form_sector.error_text = None
        self.form_employee.error_text = None
        
        # Limpa campos
        self.form_nome.value = ""
        self.form_category.value = None
        self.form_sector.value = None
        self.form_status.value = "Disponível"
        self.form_employee.value = None
        self.form_employee.visible = False
        self.form_nf.value = ""
        self.form_garantia.value = ""
        self.form_obs.value = ""
        self.date_text.value = "Nenhuma data selecionada"
        self.date_text.italic = True
        self._reset_nf_upload()

        self._show_form_modal("Cadastrar Patrimônio")

    def _open_edit_dialog(self, asset):
        self.editing_asset = asset
        self.selected_date = asset.data_compra
        
        # Garante a atualização mais recente das opções
        self.load_dropdowns()
        
        options = [
            ft.dropdown.Option("Disponível"),
            ft.dropdown.Option("Em uso"),
            ft.dropdown.Option("Baixado"),
        ]
        if asset.status == "Em manutenção":
            options.append(ft.dropdown.Option("Em manutenção"))
        self.form_status.options = options
        
        # Limpa erros visuais de validação anteriores
        self.form_nome.error_text = None
        self.form_category.error_text = None
        self.form_sector.error_text = None
        self.form_employee.error_text = None
        
        self.form_nome.value = asset.nome
        self.form_category.value = str(asset.categoria_id)
        self.form_sector.value = str(asset.setor_id)
        self.form_status.value = asset.status
        self.form_employee.value = str(asset.funcionario_id) if asset.funcionario_id else None
        self.form_employee.visible = (asset.status == "Em uso")
        self.form_nf.value = asset.nota_fiscal or ""
        self.form_garantia.value = str(asset.garantia_meses) if asset.garantia_meses is not None else ""
        self.form_obs.value = asset.observacoes or ""
        
        if asset.data_compra:
            self.date_text.value = asset.data_compra.strftime("%d/%m/%Y")
            self.date_text.italic = False
        else:
            self.date_text.value = "Nenhuma data selecionada"
            self.date_text.italic = True
        self._reset_nf_upload()

        self._show_form_modal(f"Editar Patrimônio - {asset.numero_patrimonial}")

    def _reset_nf_upload(self):
        self.selected_nf_path = None
        self.nf_file_text.value = "Nenhum arquivo anexado"
        self.nf_file_text.italic = True
        self.nf_file_text.weight = None
        self.nf_file_text.color = ft.Colors.ON_SURFACE_VARIANT

    def _show_form_modal(self, title: str):
        def close_dialog(e):
            dialog.open = False
            try:
                self.page.update()
            except RuntimeError:
                pass

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    self.form_nome,
                    ft.Row([self.form_category, self.form_sector], spacing=10),
                    ft.Row([self.form_status, self.form_employee], spacing=10),
                    ft.Row([
                        self.date_btn,
                        self.date_text
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([self.form_nf, self.nf_upload_btn], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    self.nf_file_text,
                    self.form_garantia,
                    self.form_obs,
                ], spacing=12, scroll=ft.ScrollMode.AUTO),
                width=550,
                height=480
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Salvar", on_click=lambda e: self._save_form(dialog), bgcolor=ft.Colors.BLUE_400, color=ft.Colors.WHITE)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        if dialog not in self.page.overlay:
            self.page.overlay.append(dialog)
        self.page.dialog = dialog
        dialog.open = True
        try:
            self.page.update()
        except RuntimeError:
            pass

    def _save_form(self, dialog):
        nome = self.form_nome.value.strip() if self.form_nome.value else ""
        cat_val = self.form_category.value
        sec_val = self.form_sector.value
        status = self.form_status.value
        emp_val = self.form_employee.value
        nf = self.form_nf.value.strip() if self.form_nf.value else None
        garantia_str = self.form_garantia.value.strip() if self.form_garantia.value else ""
        obs = self.form_obs.value.strip() if self.form_obs.value else None
        
        has_error = False
        
        if not nome:
            self.form_nome.error_text = "Informe o nome do patrimônio."
            has_error = True
        else:
            self.form_nome.error_text = None
            
        if not cat_val:
            self.form_category.error_text = "Selecione a Categoria."
            has_error = True
        else:
            self.form_category.error_text = None
            
        if not sec_val:
            self.form_sector.error_text = "Selecione o Setor."
            has_error = True
        else:
            self.form_sector.error_text = None
            
        if status == "Em uso" and not emp_val:
            self.form_employee.error_text = "Selecione o Funcionário."
            has_error = True
        else:
            self.form_employee.error_text = None

        if has_error:
            try:
                dialog.content.update()
            except RuntimeError:
                pass
            show_error_snackbar(self.page, "Por favor, preencha os campos obrigatórios destacados em vermelho.")
            return
            
        categoria_id = int(cat_val)
        setor_id = int(sec_val)
        funcionario_id = int(emp_val) if emp_val and status == "Em uso" else None
        
        garantia_meses = None
        if garantia_str:
            try:
                garantia_meses = int(garantia_str)
                if garantia_meses < 0:
                    show_error_snackbar(self.page, "A garantia não pode ser negativa.")
                    return
            except ValueError:
                show_error_snackbar(self.page, "Garantia deve ser um número inteiro válido.")
                return
                
        # Cria ou edita via controller
        if self.editing_asset is None:
            success, res = self.controller.create_asset(
                nome=nome,
                categoria_id=categoria_id,
                setor_id=setor_id,
                funcionario_id=funcionario_id,
                data_compra=self.selected_date,
                nota_fiscal=nf,
                garantia_meses=garantia_meses,
                status=status,
                observacoes=obs
            )
        else:
            success, res = self.controller.update_asset(
                asset_id=self.editing_asset.id,
                nome=nome,
                categoria_id=categoria_id,
                setor_id=setor_id,
                funcionario_id=funcionario_id,
                data_compra=self.selected_date,
                nota_fiscal=nf,
                garantia_meses=garantia_meses,
                status=status,
                observacoes=obs
            )
            
        if success:
            if self.selected_nf_path:
                att_success, att_res = self.controller.add_attachment(
                    source_path=self.selected_nf_path,
                    tipo_documento="Nota Fiscal",
                    asset_id=res.id
                )
                if not att_success:
                    show_error_snackbar(self.page, f"Patrimônio salvo, mas falhou ao anexar a nota fiscal: {att_res}")
            show_success_snackbar(self.page, "Patrimônio salvo com sucesso!")
            dialog.open = False
            try:
                self.page.update()
            except RuntimeError:
                pass
            self.refresh_table()
        else:
            show_error_snackbar(self.page, res)

    async def _generate_label(self, e):
        asset_id = e.control.data
        success, res = self.controller.generate_label(asset_id)
        if success:
            await reveal_file(self.page, res, desktop_message=f"Etiqueta gerada em: {res}", web_message="Etiqueta gerada!")
        else:
            show_error_snackbar(self.page, res)

    def _delete_confirm(self, asset_id: int, asset_name: str, asset_num: str):
        show_confirm_dialog(
            self.page,
            "Confirmar Exclusão Física",
            f"Atenção: Você deseja realmente EXCLUIR FISICAMENTE o patrimônio [{asset_num}] {asset_name}?\n\nEsta ação apagará em cascata todo o histórico de manutenções e anexos vinculados a este bem e NÃO poderá ser desfeita.",
            lambda: self._delete_asset(asset_id)
        )

    def _delete_asset(self, asset_id: int):
        success, message = self.controller.delete_asset(asset_id)
        if success:
            show_success_snackbar(self.page, message)
            self.refresh_table()
        else:
            show_error_snackbar(self.page, message)
