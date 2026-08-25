import flet as ft

class CustomTable(ft.Column):
    def __init__(self, columns: list[str], row_builder_func, rows_per_page: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.columns_titles = columns
        self.row_builder_func = row_builder_func
        self.rows_per_page = rows_per_page
        self.current_page = 1
        self.rows_data = []
        
        # Cria as colunas Flet
        flet_columns = [
            ft.DataColumn(ft.Text(title, weight=ft.FontWeight.BOLD, size=13)) 
            for title in self.columns_titles
        ]
        
        self.table = ft.DataTable(
            columns=flet_columns,
            rows=[],
            border_radius=8,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGH,
            divider_thickness=1,
            horizontal_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            column_spacing=24,
            expand=True
        )
        
        self.page_info = ft.Text("", size=13, color=ft.Colors.ON_SURFACE_VARIANT)
        
        self.prev_btn = ft.IconButton(
            ft.Icons.NAVIGATE_BEFORE_ROUNDED,
            on_click=self._prev_page,
            disabled=True,
            icon_size=20,
            tooltip="Página anterior"
        )
        self.next_btn = ft.IconButton(
            ft.Icons.NAVIGATE_NEXT_ROUNDED,
            on_click=self._next_page,
            disabled=True,
            icon_size=20,
            tooltip="Próxima página"
        )
        
        self.pagination_row = ft.Row([
            self.page_info,
            ft.Row([self.prev_btn, self.next_btn], spacing=5)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Envolve a tabela num ListView ou Container com rolagem horizontal para telas estreitas
        self.controls = [
            ft.Container(
                content=ft.Row([self.table], scroll=ft.ScrollMode.ALWAYS, expand=True),
                border_radius=8,
                bgcolor=ft.Colors.SURFACE,
                padding=10,
                expand=True
            ),
            self.pagination_row
        ]
        self.spacing = 10
        self.expand = True
        
    def update_data(self, new_data: list):
        self.rows_data = new_data
        # Reseta para a primeira página ao atualizar dados
        self.current_page = 1
        self._render_page()
        
    def _render_page(self):
        total_items = len(self.rows_data)
        total_pages = max(1, (total_items + self.rows_per_page - 1) // self.rows_per_page)
        
        if self.current_page > total_pages:
            self.current_page = total_pages
            
        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, total_items)
        
        page_items = self.rows_data[start_idx:end_idx]
        
        self.table.rows = [self.row_builder_func(item) for item in page_items]
        
        # Atualiza controles de navegação
        self.prev_btn.disabled = (self.current_page == 1)
        self.next_btn.disabled = (self.current_page == total_pages)
        
        if total_items == 0:
            self.page_info.value = "Nenhum registro encontrado"
        else:
            self.page_info.value = f"Exibindo {start_idx + 1}-{end_idx} de {total_items} registros (Página {self.current_page}/{total_pages})"
            
        try:
            self.table.update()
        except RuntimeError:
            pass
        try:
            self.update()
        except RuntimeError:
            pass
        
    def _prev_page(self, e):
        if self.current_page > 1:
            self.current_page -= 1
            self._render_page()
            
    def _next_page(self, e):
        total_items = len(self.rows_data)
        total_pages = (total_items + self.rows_per_page - 1) // self.rows_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self._render_page()
