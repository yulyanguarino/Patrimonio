import flet as ft
from datetime import datetime, date
from views.base_view import BaseView
from controllers.maintenance_controller import MaintenanceController
from controllers.asset_controller import AssetController
from components.custom_table import CustomTable
from components.dialogs import show_error_snackbar, show_success_snackbar, show_confirm_dialog

class MaintenanceView(BaseView):
    def __init__(self, page: ft.Page, db, navigate_to, **kwargs):
        super().__init__(page, **kwargs)
        self.db = db
        self.navigate_to = navigate_to
        self.controller = MaintenanceController(db)
        self.asset_controller = AssetController(db)
        
        self.start_date = None
        self.end_date = None
        self.selected_maint_date = date.today()
        
        # DatePickers para Filtro
        self.start_date_picker = ft.DatePicker(on_change=self._on_start_date_selected)
        self.end_date_picker = ft.DatePicker(on_change=self._on_end_date_selected)
        self.maint_date_picker = ft.DatePicker(on_change=self._on_maint_date_selected)
        
        for dp in [self.start_date_picker, self.end_date_picker, self.maint_date_picker]:
            if dp not in self.page.overlay:
                self.page.overlay.append(dp)
            
        # Elementos da UI
        self.title_text = ft.Text("Histórico Global de Manutenções", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
        
        # Filtros
        self.search_asset = ft.TextField(
            label="Pesquisar por patrimônio ou plaqueta",
            expand=True,
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            on_change=self._trigger_search,
            border_radius=8
        )
        
        self.filter_type = ft.Dropdown(
            label="Tipo de Manutenção",
            width=180,
            options=[
                ft.dropdown.Option("", "Todos"),
                ft.dropdown.Option("Preventiva"),
                ft.dropdown.Option("Corretiva"),
            ],
            value="",
            on_select=self._trigger_search,
            border_radius=8
        )
        
        self.start_date_btn = ft.OutlinedButton(
            "Data Inicial",
            icon=ft.Icons.DATE_RANGE_ROUNDED,
            on_click=self._open_start_date_picker,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )
        self.end_date_btn = ft.OutlinedButton(
            "Data Final",
            icon=ft.Icons.DATE_RANGE_ROUNDED,
            on_click=self._open_end_date_picker,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )
        
        self.clear_dates_btn = ft.IconButton(
            ft.Icons.CLEAR_ROUNDED,
            tooltip="Limpar datas",
            on_click=self._clear_dates
        )
        
        self.new_maint_btn = ft.ElevatedButton(
            "Nova Manutenção",
            icon=ft.Icons.ADD_ROUNDED,
            on_click=self._open_create_maintenance_dialog,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.BLUE_400,
                color=ft.Colors.WHITE
            )
        )
        
        self.filter_row = ft.Row([
            self.search_asset,
            self.filter_type,
            self.start_date_btn,
            self.end_date_btn,
            self.clear_dates_btn,
            self.new_maint_btn
        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Tabela Custom Table
        self.table = CustomTable(
            columns=["Patrimônio", "Tipo", "Data da Manutenção", "Prestador de Serviço", "Valor Gasto", "Ações"],
            row_builder_func=self._build_row,
            rows_per_page=10
        )
        
        self.content = ft.Column([
            self.title_text,
            ft.Text("Acompanhe os custos e intervenções preventivas ou corretivas realizadas nos bens patrimoniais.", color=ft.Colors.ON_SURFACE_VARIANT, size=14),
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            self.filter_row,
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            self.table
        ], expand=True, spacing=10)
        
        # Campos do Formulário Modal (Registrar Nova Manutenção)
        self.form_asset = ft.Dropdown(label="Patrimônio*", hint_text="Selecione o Patrimônio", border_radius=8, expand=True)
        self.form_tipo = ft.Dropdown(
            label="Tipo de Manutenção*",
            options=[
                ft.dropdown.Option("Corretiva"),
                ft.dropdown.Option("Preventiva"),
            ],
            value="Corretiva",
            border_radius=8,
            expand=True
        )
        self.form_prestador = ft.TextField(label="Prestador de Serviço / Técnico*", border_radius=8)
        self.form_valor = ft.TextField(label="Valor Gasto (R$)*", value="0.00", keyboard_type=ft.KeyboardType.NUMBER, border_radius=8)
        self.form_descricao = ft.TextField(label="Descrição do Problema*", multiline=True, min_lines=2, max_lines=3, border_radius=8)
        self.form_servico = ft.TextField(label="Serviço Executado*", multiline=True, min_lines=2, max_lines=3, border_radius=8)
        self.form_obs = ft.TextField(label="Observações", multiline=True, min_lines=2, max_lines=3, border_radius=8)
        self.form_set_status = ft.Checkbox(label="Alterar status do patrimônio para 'Em manutenção'", value=True)
        
        self.maint_date_btn = ft.OutlinedButton(
            "Data da Manutenção",
            icon=ft.Icons.CALENDAR_MONTH_ROUNDED,
            on_click=self._open_maint_date_picker
        )
        self.maint_date_text = ft.Text(date.today().strftime("%d/%m/%Y"), size=13, weight=ft.FontWeight.W_500)

    def on_mount(self) -> None:
        self.refresh_table()

    def _open_start_date_picker(self, e):
        self.start_date_picker.open = True
        try:
            self.page.update()
        except RuntimeError:
            pass

    def _open_end_date_picker(self, e):
        self.end_date_picker.open = True
        try:
            self.page.update()
        except RuntimeError:
            pass

    def _open_maint_date_picker(self, e):
        self.maint_date_picker.open = True
        try:
            self.page.update()
        except RuntimeError:
            pass

    def _on_start_date_selected(self, e):
        if self.start_date_picker.value:
            val = self.start_date_picker.value
            self.start_date = val.date() if hasattr(val, "date") else val
            self.start_date_btn.text = self.start_date.strftime("%d/%m/%Y")
            try:
                self.start_date_btn.update()
            except RuntimeError:
                pass
            self.refresh_table()

    def _on_end_date_selected(self, e):
        if self.end_date_picker.value:
            val = self.end_date_picker.value
            self.end_date = val.date() if hasattr(val, "date") else val
            self.end_date_btn.text = self.end_date.strftime("%d/%m/%Y")
            try:
                self.end_date_btn.update()
            except RuntimeError:
                pass
            self.refresh_table()

    def _on_maint_date_selected(self, e):
        if self.maint_date_picker.value:
            val = self.maint_date_picker.value
            self.selected_maint_date = val.date() if hasattr(val, "date") else val
            self.maint_date_text.value = self.selected_maint_date.strftime("%d/%m/%Y")
            try:
                self.maint_date_text.update()
            except RuntimeError:
                pass

    def _clear_dates(self, e):
        self.start_date = None
        self.end_date = None
        self.start_date_btn.text = "Data Inicial"
        self.end_date_btn.text = "Data Final"
        try:
            self.start_date_btn.update()
        except RuntimeError:
            pass
        try:
            self.end_date_btn.update()
        except RuntimeError:
            pass
        self.refresh_table()

    def _trigger_search(self, e):
        self.refresh_table()

    def refresh_table(self):
        maint_type = self.filter_type.value or None
        
        maints = self.controller.list_maintenances(
            start_date=self.start_date,
            end_date=self.end_date,
            maintenance_type=maint_type
        )
        
        query = self.search_asset.value.strip().lower() if self.search_asset.value else ""
        if query:
            filtered = []
            for m in maints:
                asset_code = m.asset.numero_patrimonial.lower() if m.asset else ""
                asset_name = m.asset.nome.lower() if m.asset else ""
                prestador = m.prestador.lower() if m.prestador else ""
                if query in asset_code or query in asset_name or query in prestador:
                    filtered.append(m)
            maints = filtered
            
        self.table.update_data(maints)

    def _open_create_maintenance_dialog(self, e):
        # Carrega lista atualizada de patrimônios ativos (não baixados)
        all_assets = self.asset_controller.search_assets()
        active_assets = [a for a in all_assets if a.status != "Baixado"]
        
        self.form_asset.options = [
            ft.dropdown.Option(str(a.id), f"[{a.numero_patrimonial}] {a.nome} ({a.status})")
            for a in active_assets
        ]
        
        # Limpa erros visuais e valores
        self.form_asset.error_text = None
        self.form_tipo.error_text = None
        self.form_prestador.error_text = None
        self.form_valor.error_text = None
        self.form_descricao.error_text = None
        self.form_servico.error_text = None
        
        self.form_asset.value = None
        self.form_tipo.value = "Corretiva"
        self.form_prestador.value = ""
        self.form_valor.value = "0.00"
        self.form_descricao.value = ""
        self.form_servico.value = ""
        self.form_obs.value = ""
        self.form_set_status.value = True
        self.selected_maint_date = date.today()
        self.maint_date_text.value = self.selected_maint_date.strftime("%d/%m/%Y")
        
        self._show_maintenance_modal("Registrar Nova Manutenção")

    def _show_maintenance_modal(self, title: str):
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
                    ft.Row([self.form_asset, self.form_tipo], spacing=10),
                    self.form_prestador,
                    self.form_valor,
                    ft.Row([
                        self.maint_date_btn,
                        self.maint_date_text
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    self.form_descricao,
                    self.form_servico,
                    self.form_obs,
                    self.form_set_status,
                ], spacing=12, scroll=ft.ScrollMode.AUTO),
                width=580,
                height=520
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Salvar Manutenção", on_click=lambda e: self._save_maintenance_form(dialog), bgcolor=ft.Colors.BLUE_400, color=ft.Colors.WHITE)
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

    def _save_maintenance_form(self, dialog):
        asset_val = self.form_asset.value
        tipo = self.form_tipo.value
        prestador = self.form_prestador.value.strip() if self.form_prestador.value else ""
        valor_str = self.form_valor.value.strip() if self.form_valor.value else "0"
        descricao = self.form_descricao.value.strip() if self.form_descricao.value else ""
        servico = self.form_servico.value.strip() if self.form_servico.value else ""
        obs = self.form_obs.value.strip() if self.form_obs.value else None
        set_status = self.form_set_status.value
        
        has_error = False
        
        if not asset_val:
            self.form_asset.error_text = "Selecione o Patrimônio."
            has_error = True
        else:
            self.form_asset.error_text = None
            
        if not prestador:
            self.form_prestador.error_text = "Informe o Prestador / Técnico."
            has_error = True
        else:
            self.form_prestador.error_text = None
            
        if not descricao:
            self.form_descricao.error_text = "Descreva o problema constatado."
            has_error = True
        else:
            self.form_descricao.error_text = None
            
        if not servico:
            self.form_servico.error_text = "Descreva o serviço executado."
            has_error = True
        else:
            self.form_servico.error_text = None

        valor_gasto = 0.0
        try:
            valor_gasto = float(valor_str.replace(",", "."))
            if valor_gasto < 0:
                self.form_valor.error_text = "O valor não pode ser negativo."
                has_error = True
            else:
                self.form_valor.error_text = None
        except ValueError:
            self.form_valor.error_text = "Informe um valor numérico válido."
            has_error = True

        if has_error:
            try:
                dialog.content.update()
            except RuntimeError:
                pass
            show_error_snackbar(self.page, "Por favor, preencha os campos obrigatórios destacados em vermelho.")
            return

        patrimonio_id = int(asset_val)
        success, res = self.controller.register_maintenance(
            patrimonio_id=patrimonio_id,
            tipo=tipo,
            data_manutencao=self.selected_maint_date,
            prestador=prestador,
            descricao_problema=descricao,
            servico_executado=servico,
            valor_gasto=valor_gasto,
            observacoes=obs,
            set_asset_in_maintenance=set_status
        )

        if success:
            show_success_snackbar(self.page, "Manutenção registrada com sucesso!")
            dialog.open = False
            try:
                self.page.update()
            except RuntimeError:
                pass
            self.refresh_table()
        else:
            show_error_snackbar(self.page, res)

    def _conclude_maintenance_confirm(self, asset):
        show_confirm_dialog(
            self.page,
            "Concluir Manutenção",
            f"Deseja finalizar o reparo e retornar o patrimônio [{asset.numero_patrimonial}] {asset.nome} para o status 'Disponível'?",
            lambda: self._conclude_maintenance(asset.id)
        )

    def _conclude_maintenance(self, asset_id: int):
        success, message = self.controller.conclude_maintenance(asset_id)
        if success:
            show_success_snackbar(self.page, message)
            self.refresh_table()
        else:
            show_error_snackbar(self.page, message)

    def _build_row(self, maint):
        type_color = ft.Colors.AMBER_700 if maint.tipo == "Corretiva" else ft.Colors.BLUE_700
        asset_info = f"[{maint.asset.numero_patrimonial}] {maint.asset.nome}" if maint.asset else "-"
        in_maintenance = maint.asset and maint.asset.status == "Em manutenção"
        
        actions = [
            ft.IconButton(
                ft.Icons.INFO_OUTLINE_ROUNDED,
                tooltip="Detalhes do Patrimônio",
                on_click=lambda e: self.navigate_to("/asset-detail", asset_id=maint.patrimonio_id)
            )
        ]
        
        if in_maintenance:
            actions.append(
                ft.IconButton(
                    ft.Icons.CHECK_CIRCLE_ROUNDED,
                    icon_color=ft.Colors.GREEN_400,
                    tooltip="Concluir Manutenção (Retornar bem para Disponível)",
                    on_click=lambda e, a=maint.asset: self._conclude_maintenance_confirm(a)
                )
            )
        
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(asset_info, weight=ft.FontWeight.W_500)),
                ft.DataCell(ft.Container(
                    content=ft.Text(maint.tipo, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=type_color,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                    border_radius=4
                )),
                ft.DataCell(ft.Text(maint.data_manutencao.strftime("%d/%m/%Y"))),
                ft.DataCell(ft.Text(maint.prestador)),
                ft.DataCell(ft.Text(f"R$ {maint.valor_gasto:,.2f}", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)),
                ft.DataCell(ft.Row(actions, spacing=0))
            ]
        )
