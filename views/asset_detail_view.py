import flet as ft
import os
from datetime import datetime, date
from views.base_view import BaseView
from controllers.asset_controller import AssetController
from controllers.maintenance_controller import MaintenanceController
from components.file_uploader import FileUploader
from components.dialogs import show_success_snackbar, show_error_snackbar, show_confirm_dialog, show_info_dialog
from utils.file_actions import reveal_file

class AssetDetailView(BaseView):
    def __init__(self, page: ft.Page, db, navigate_to, asset_id: int = None, **kwargs):
        super().__init__(page, **kwargs)
        self.db = db
        self.navigate_to = navigate_to
        self.asset_id = asset_id
        
        self.controller = AssetController(db)
        self.maint_controller = MaintenanceController(db)
        
        self.selected_maint_date = date.today()
        self.selected_next_date = None
        
        # DatePickers para as manutenções
        self.maint_date_picker = ft.DatePicker(
            value=datetime.now(),
            on_change=self._on_maint_date_selected
        )
        self.next_date_picker = ft.DatePicker(
            on_change=self._on_next_date_selected
        )
        if self.maint_date_picker not in self.page.overlay:
            self.page.overlay.append(self.maint_date_picker)
        if self.next_date_picker not in self.page.overlay:
            self.page.overlay.append(self.next_date_picker)
            
        # Caso o asset_id não seja fornecido
        if not asset_id:
            self.content = ft.Column([
                ft.Text("Erro: Nenhum patrimônio selecionado.", size=18, color=ft.Colors.RED_400),
                ft.ElevatedButton("Voltar para Listagem", on_click=lambda _: self.navigate_to("/assets"))
            ])
            return
            
        # Layout Básico
        self.back_btn = ft.IconButton(
            ft.Icons.ARROW_BACK_ROUNDED,
            tooltip="Voltar para listagem",
            on_click=lambda _: self.navigate_to("/assets")
        )
        self.title_text = ft.Text("Detalhes do Patrimônio", size=24, weight=ft.FontWeight.BOLD)
        self.subtitle_text = ft.Text("", size=14, color=ft.Colors.ON_SURFACE_VARIANT)
        self.label_btn = ft.ElevatedButton(
            "Gerar Etiqueta",
            icon=ft.Icons.QR_CODE_2_ROUNDED,
            on_click=self._on_generate_label,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.BLUE_400,
                color=ft.Colors.WHITE
            )
        )
        
        # Cartões de Informação do Patrimônio
        self.info_grid = ft.GridView(
            runs_count=3,
            max_extent=350,
            child_aspect_ratio=3.0,
            spacing=15,
            run_spacing=15,
            expand=False
        )
        
        # Upload de arquivos
        self.uploader = FileUploader(self.page, on_file_selected=self._on_file_selected)
        self.attachments_list = ft.Column(spacing=8)
        
        # Histórico de manutenção
        self.maint_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        self.new_maint_btn = ft.ElevatedButton(
            "Registrar Manutenção",
            icon=ft.Icons.ADD_ROUNDED,
            on_click=self._open_maint_dialog,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.BLUE_400,
                color=ft.Colors.WHITE
            )
        )
        
        # Conteúdo da aba 1: Manutenções
        self.maint_tab_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Registro de Intervenções e Consertos", size=16, weight=ft.FontWeight.BOLD),
                    self.new_maint_btn
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.maint_list
            ], expand=True),
            padding=ft.Padding.only(top=15),
            expand=True
        )

        # Conteúdo da aba 2: Anexos
        self.attachments_tab_content = ft.Container(
            content=ft.Column([
                ft.Text("Upload de Documentos (Notas Fiscais, Manuais, Fotos)", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                self.uploader,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.attachments_list
            ], expand=True),
            padding=ft.Padding.only(top=15),
            expand=True
        )

        self.active_tab = "maintenances"
        self.tab_container = ft.Container(
            content=self.maint_tab_content,
            expand=True
        )

        self.btn_tab_maint = ft.ElevatedButton(
            "Histórico de Manutenções",
            icon=ft.Icons.BUILD_ROUNDED,
            on_click=lambda e: self._switch_tab("maintenances"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.BLUE_900,
                color=ft.Colors.WHITE
            )
        )
        self.btn_tab_attach = ft.ElevatedButton(
            "Anexos e Documentos",
            icon=ft.Icons.ATTACH_FILE_ROUNDED,
            on_click=lambda e: self._switch_tab("attachments"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                color=ft.Colors.WHITE
            )
        )

        self.tabs_row = ft.Row([
            self.btn_tab_maint,
            self.btn_tab_attach
        ], spacing=10)
        
        self.content = ft.Column([
            ft.Row([self.back_btn, self.title_text, ft.Container(expand=True), self.label_btn], spacing=10),
            self.subtitle_text,
            ft.Divider(height=10, color=ft.Colors.OUTLINE_VARIANT),
            self.info_grid,
            ft.Divider(height=10, color=ft.Colors.OUTLINE_VARIANT),
            self.tabs_row,
            self.tab_container
        ], expand=True, spacing=10)
        
        self.maint_tipo = ft.Dropdown(
            label="Tipo*",
            options=[
                ft.dropdown.Option("Preventiva"),
                ft.dropdown.Option("Corretiva"),
            ],
            value="Corretiva",
            border_radius=8,
            expand=True
        )
        self.maint_date_btn = ft.OutlinedButton(
            "Data da Manutenção*",
            icon=ft.Icons.CALENDAR_MONTH_ROUNDED,
            on_click=self._open_maint_date_picker
        )
        self.maint_date_text = ft.Text(date.today().strftime("%d/%m/%Y"), size=13, weight=ft.FontWeight.BOLD)
        
        self.maint_prestador = ft.TextField(label="Prestador de Serviço*", border_radius=8)
        self.maint_problema = ft.TextField(label="Descrição do Problema*", border_radius=8)
        self.maint_servico = ft.TextField(label="Serviço Executado*", border_radius=8)
        self.maint_valor = ft.TextField(label="Valor Gasto (R$)*", keyboard_type=ft.KeyboardType.NUMBER, value="0.00", border_radius=8)
        
        self.next_date_btn = ft.OutlinedButton(
            "Próxima Manutenção",
            icon=ft.Icons.CALENDAR_MONTH_ROUNDED,
            on_click=self._open_next_date_picker
        )
        self.next_date_text = ft.Text("Não planejada", size=13, italic=True)
        
        self.maint_obs = ft.TextField(label="Observações Adicionais", multiline=True, min_lines=2, max_lines=4, border_radius=8)
        self.maint_chk_status = ft.Checkbox(label="Alterar status do bem para 'Em manutenção'", value=True)

    def _open_maint_date_picker(self, e):
        if self.maint_date_picker not in self.page.overlay:
            self.page.overlay.append(self.maint_date_picker)
        self.maint_date_picker.open = True
        try:
            self.page.update()
        except RuntimeError:
            pass

    def _open_next_date_picker(self, e):
        if self.next_date_picker not in self.page.overlay:
            self.page.overlay.append(self.next_date_picker)
        self.next_date_picker.open = True
        try:
            self.page.update()
        except RuntimeError:
            pass

    def _switch_tab(self, tab_name: str):
        self.active_tab = tab_name
        if tab_name == "maintenances":
            self.tab_container.content = self.maint_tab_content
            self.btn_tab_maint.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.BLUE_900,
                color=ft.Colors.WHITE
            )
            self.btn_tab_attach.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                color=ft.Colors.WHITE
            )
        else:
            self.tab_container.content = self.attachments_tab_content
            self.btn_tab_maint.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                color=ft.Colors.WHITE
            )
            self.btn_tab_attach.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.BLUE_900,
                color=ft.Colors.WHITE
            )
            
        try:
            self.btn_tab_maint.update()
        except RuntimeError:
            pass
        try:
            self.btn_tab_attach.update()
        except RuntimeError:
            pass
        try:
            self.tab_container.update()
        except RuntimeError:
            pass

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self):
        asset = self.controller.get_asset(self.asset_id)
        if not asset:
            show_error_snackbar(self.page, "Patrimônio não localizado.")
            self.navigate_to("/assets")
            return
            
        self.title_text.value = f"[{asset.numero_patrimonial}] {asset.nome}"
        self.subtitle_text.value = f"Criado em {asset.criado_em.strftime('%d/%m/%Y %H:%M')}"
        
        # Monta os cartões de informação
        status_colors = {
            "Disponível": ft.Colors.GREEN_400,
            "Em uso": ft.Colors.BLUE_400,
            "Em manutenção": ft.Colors.AMBER_400,
            "Baixado": ft.Colors.RED_400
        }
        status_color = status_colors.get(asset.status, ft.Colors.ON_SURFACE)
        
        self.info_grid.controls = [
            self._build_info_card("Status Atual", asset.status, ft.Icons.INFO_ROUNDED, status_color),
            self._build_info_card("Categoria", asset.category.nome if asset.category else "-", ft.Icons.CATEGORY_ROUNDED, ft.Colors.BLUE_200),
            self._build_info_card("Setor Alocado", asset.sector.nome if asset.sector else "-", ft.Icons.BUSINESS_CENTER_ROUNDED, ft.Colors.BLUE_200),
            self._build_info_card("Responsável", asset.employee.nome if asset.employee else "Nenhum", ft.Icons.PERSON_ROUNDED, ft.Colors.PURPLE_200),
            self._build_info_card("Data de Compra", asset.data_compra.strftime("%d/%m/%Y") if asset.data_compra else "-", ft.Icons.CALENDAR_MONTH_ROUNDED, ft.Colors.GREEN_200),
            self._build_info_card("Garantia", f"{asset.garantia_meses} meses" if asset.garantia_meses else "-", ft.Icons.SHIELD_ROUNDED, ft.Colors.GREEN_200),
            self._build_info_card("Nota Fiscal", asset.nota_fiscal or "-", ft.Icons.RECEIPT_ROUNDED, ft.Colors.GREY_400),
            self._build_info_card(
                "Observações", asset.observacoes or "-", ft.Icons.NOTE_ROUNDED, ft.Colors.GREY_400,
                on_click=(lambda e, texto=asset.observacoes: self._show_full_text("Observações", texto)) if asset.observacoes else None
            ),
        ]
        
        # Desabilita botões de manutenção caso o patrimônio esteja baixado
        if asset.status == "Baixado":
            self.new_maint_btn.disabled = True
            self.uploader.disabled = True
        else:
            self.new_maint_btn.disabled = False
            self.uploader.disabled = False
            
        try:
            self.info_grid.update()
        except RuntimeError:
            pass
        try:
            self.title_text.update()
        except RuntimeError:
            pass
        try:
            self.subtitle_text.update()
        except RuntimeError:
            pass
        try:
            self.new_maint_btn.update()
        except RuntimeError:
            pass
        
        # Atualiza anexos
        self.refresh_attachments(asset.attachments, is_baixado=(asset.status == "Baixado"))
        
        # Atualiza manutenções
        self.refresh_maintenances(asset.maintenances)

    def _build_info_card(self, title: str, value: str, icon: str, icon_color: str, on_click=None):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=icon_color, size=22),
                ft.Column([
                    ft.Text(title, size=11, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500),
                    ft.Text(value, size=14, weight=ft.FontWeight.BOLD, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ], spacing=1, expand=True),
                ft.Icon(ft.Icons.OPEN_IN_FULL_ROUNDED, size=14, color=ft.Colors.ON_SURFACE_VARIANT) if on_click else ft.Container(),
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding.symmetric(horizontal=15, vertical=10),
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=8,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            on_click=on_click,
            ink=bool(on_click),
            tooltip="Clique para ver o texto completo" if on_click else None,
        )

    def _show_full_text(self, title: str, text: str):
        show_info_dialog(self.page, title, text)

    def refresh_attachments(self, attachments, is_baixado: bool = False):
        self.attachments_list.controls.clear()
        if not attachments:
            self.attachments_list.controls.append(
                ft.Text("Nenhum documento ou anexo vinculado.", italic=True, size=13, color=ft.Colors.ON_SURFACE_VARIANT)
            )
        else:
            for att in attachments:
                self.attachments_list.controls.append(self._build_attachment_row(att, is_baixado))
        try:
            self.attachments_list.update()
        except RuntimeError:
            pass

    def _build_attachment_row(self, attachment, is_baixado: bool):
        # Determina ícone pelo tipo do arquivo
        ext = os.path.splitext(attachment.nome_arquivo)[1].lower()
        if ext in (".jpg", ".jpeg", ".png", ".webp"):
            icon = ft.Icons.IMAGE_ROUNDED
            color = ft.Colors.BLUE_400
        elif ext == ".pdf":
            icon = ft.Icons.PICTURE_AS_PDF_ROUNDED
            color = ft.Colors.RED_400
        else:
            icon = ft.Icons.INSERT_DRIVE_FILE_ROUNDED
            color = ft.Colors.GREY_400

        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color, size=20),
                ft.Column([
                    ft.Text(attachment.nome_arquivo, size=13, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Tipo: {attachment.tipo_documento}", size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                ], expand=True, spacing=1),
                ft.IconButton(
                    ft.Icons.OPEN_IN_NEW_ROUNDED,
                    tooltip="Abrir Documento",
                    data=attachment.caminho_local,
                    on_click=self._open_file
                ),
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE_ROUNDED,
                    icon_color=ft.Colors.RED_400,
                    tooltip="Excluir Anexo",
                    disabled=is_baixado,
                    on_click=lambda _: self._confirm_delete_attachment(attachment.id)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_radius=8
        )

    async def _open_file(self, e):
        path = e.control.data
        if not await reveal_file(self.page, path, web_title="Anexo pronto!"):
            show_error_snackbar(self.page, "Arquivo físico não foi localizado no disco.")

    def _confirm_delete_attachment(self, attachment_id: int):
        show_confirm_dialog(
            self.page,
            "Confirmar Remoção",
            "Deseja realmente remover este anexo? O arquivo correspondente será excluído do disco definitivamente.",
            lambda: self._delete_attachment(attachment_id)
        )

    def _delete_attachment(self, attachment_id: int):
        success, message = self.controller.delete_attachment(attachment_id)
        if success:
            show_success_snackbar(self.page, message)
            self.refresh_data()
        else:
            show_error_snackbar(self.page, message)

    async def _on_generate_label(self, e):
        success, res = self.controller.generate_label(self.asset_id)
        if success:
            await reveal_file(self.page, res, desktop_message=f"Etiqueta gerada em: {res}", web_title="Etiqueta gerada!")
        else:
            show_error_snackbar(self.page, res)

    def _on_file_selected(self, source_path: str, doc_type: str):
        success, res = self.controller.add_attachment(
            source_path=source_path,
            tipo_documento=doc_type,
            asset_id=self.asset_id
        )
        if success:
            show_success_snackbar(self.page, f"Anexo '{res.nome_arquivo}' enviado com sucesso!")
            self.uploader.reset()
            self.refresh_data()
        else:
            show_error_snackbar(self.page, res)

    def refresh_maintenances(self, maintenances):
        self.maint_list.controls.clear()
        if not maintenances:
            self.maint_list.controls.append(
                ft.Text("Nenhuma manutenção registrada para este patrimônio.", italic=True, size=13, color=ft.Colors.ON_SURFACE_VARIANT)
            )
        else:
            # Ordena por data decrescente
            sorted_maints = sorted(maintenances, key=lambda m: m.data_manutencao, reverse=True)
            for m in sorted_maints:
                self.maint_list.controls.append(self._build_maintenance_card(m))
        try:
            self.maint_list.update()
        except RuntimeError:
            pass

    def _build_maintenance_card(self, maint):
        type_color = ft.Colors.AMBER_700 if maint.tipo == "Corretiva" else ft.Colors.BLUE_700
        next_maint = f" | Próxima planejada: {maint.data_proxima.strftime('%d/%m/%Y')}" if maint.data_proxima else ""
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(maint.tipo.upper(), size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        bgcolor=type_color,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                        border_radius=4
                    ),
                    ft.Text(f"Data: {maint.data_manutencao.strftime('%d/%m/%Y')}{next_maint}", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text(f"Valor: R$ {maint.valor_gasto:,.2f}", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                ft.Text(f"Prestador/Técnico: {maint.prestador}", size=13, weight=ft.FontWeight.BOLD),
                ft.Text(f"Problema: {maint.descricao_problema}", size=13),
                ft.Text(f"Serviço: {maint.servico_executado}", size=13),
                ft.Text(f"Obs: {maint.observacoes}" if maint.observacoes else "", size=12, italic=True, color=ft.Colors.ON_SURFACE_VARIANT)
            ], spacing=8),
            padding=15,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=8,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
        )

    def _on_maint_date_selected(self, e):
        if self.maint_date_picker.value:
            self.selected_maint_date = self.maint_date_picker.value.date()
            self.maint_date_text.value = self.selected_maint_date.strftime("%d/%m/%Y")
            try:
                self.maint_date_text.update()
            except RuntimeError:
                pass

    def _on_next_date_selected(self, e):
        if self.next_date_picker.value:
            self.selected_next_date = self.next_date_picker.value.date()
            self.next_date_text.value = self.selected_next_date.strftime("%d/%m/%Y")
            self.next_date_text.italic = False
            try:
                self.next_date_text.update()
            except RuntimeError:
                pass

    def _open_maint_dialog(self, e):
        self.selected_maint_date = date.today()
        self.selected_next_date = None
        
        self.maint_tipo.value = "Corretiva"
        self.maint_prestador.value = ""
        self.maint_problema.value = ""
        self.maint_servico.value = ""
        self.maint_valor.value = "0.00"
        self.maint_obs.value = ""
        self.maint_date_text.value = self.selected_maint_date.strftime("%d/%m/%Y")
        self.next_date_text.value = "Não planejada"
        self.next_date_text.italic = True
        self.maint_chk_status.value = True
        
        self._show_maint_modal()

    def _show_maint_modal(self):
        def close_dialog(e):
            dialog.open = False
            try:
                self.page.update()
            except RuntimeError:
                pass

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Registrar Manutenção", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    self.maint_tipo,
                    ft.Row([
                        self.maint_date_btn,
                        self.maint_date_text
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    self.maint_prestador,
                    self.maint_problema,
                    self.maint_servico,
                    self.maint_valor,
                    ft.Row([
                        self.next_date_btn,
                        self.next_date_text
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    self.maint_obs,
                    self.maint_chk_status
                ], spacing=12, scroll=ft.ScrollMode.AUTO),
                width=550,
                height=480
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Salvar", on_click=lambda e: self._save_maintenance(dialog), bgcolor=ft.Colors.BLUE_400, color=ft.Colors.WHITE)
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

    def _save_maintenance(self, dialog):
        tipo = self.maint_tipo.value
        prestador = self.maint_prestador.value.strip()
        problema = self.maint_problema.value.strip()
        servico = self.maint_servico.value.strip()
        valor_str = self.maint_valor.value.strip()
        obs = self.maint_obs.value.strip() or None
        set_status = self.maint_chk_status.value
        
        if not prestador or not problema or not servico or not valor_str:
            show_error_snackbar(self.page, "Por favor, preencha todos os campos obrigatórios (*).")
            return
            
        try:
            valor = float(valor_str)
            if valor < 0:
                show_error_snackbar(self.page, "O valor gasto não pode ser negativo.")
                return
        except ValueError:
            show_error_snackbar(self.page, "Valor gasto inválido.")
            return
            
        if self.selected_next_date and self.selected_next_date < self.selected_maint_date:
            show_error_snackbar(self.page, "A data da próxima manutenção não pode ser anterior à data da manutenção atual.")
            return
            
        success, res = self.maint_controller.register_maintenance(
            patrimonio_id=self.asset_id,
            tipo=tipo,
            data_manutencao=self.selected_maint_date,
            prestador=prestador,
            descricao_problema=problema,
            servico_executado=servico,
            valor_gasto=valor,
            data_proxima=self.selected_next_date,
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
            self.refresh_data()
        else:
            show_error_snackbar(self.page, res)
