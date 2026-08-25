import flet as ft

class FileUploader(ft.Container):
    def __init__(self, page: ft.Page, on_file_selected, **kwargs):
        super().__init__(**kwargs)
        self._custom_page = page
        self.on_file_selected = on_file_selected
        self.selected_path = None

    @property
    def page(self):
        return self._custom_page
        
        # O FilePicker do Flet
        self.file_picker = ft.FilePicker(on_result=self._on_picker_result)
        
        # Adiciona o FilePicker no overlay caso não exista
        if self.file_picker not in self.page.overlay:
            self.page.overlay.append(self.file_picker)
            
        self.file_name_text = ft.Text("Nenhum arquivo selecionado", size=13, italic=True, color=ft.Colors.ON_SURFACE_VARIANT)
        
        self.select_btn = ft.ElevatedButton(
            "Selecionar Arquivo",
            icon=ft.Icons.ATTACH_FILE_ROUNDED,
            on_click=lambda _: self.file_picker.pick_files(
                allow_multiple=False,
                dialog_title="Selecione o documento/anexo"
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )
        
        self.doc_type_dropdown = ft.Dropdown(
            label="Tipo de Documento",
            width=180,
            options=[
                ft.dropdown.Option("Foto"),
                ft.dropdown.Option("Nota Fiscal"),
                ft.dropdown.Option("Manual"),
                ft.dropdown.Option("Garantia"),
                ft.dropdown.Option("Outros"),
            ],
            value="Nota Fiscal",
            height=50
        )
        
        self.padding = ft.Padding.all(15)
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_LOW
        self.border_radius = 8
        self.border = ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
        
        self.content = ft.Row([
            self.select_btn,
            ft.Container(content=self.file_name_text, expand=True),
            self.doc_type_dropdown,
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        
    def _on_picker_result(self, e):
        if e.files:
            file = e.files[0]
            self.selected_path = file.path
            self.file_name_text.value = file.name
            self.file_name_text.italic = False
            self.file_name_text.weight = ft.FontWeight.BOLD
            self.file_name_text.color = ft.Colors.ON_SURFACE
            self.update()
            if self.on_file_selected:
                self.on_file_selected(self.selected_path, self.doc_type_dropdown.value)
                
    def reset(self):
        self.selected_path = None
        self.file_name_text.value = "Nenhum arquivo selecionado"
        self.file_name_text.italic = True
        self.file_name_text.weight = None
        self.file_name_text.color = ft.Colors.ON_SURFACE_VARIANT
        self.update()
