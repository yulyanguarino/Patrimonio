import flet as ft

COMPACT_BREAKPOINT = 700  # abaixo disso (celular/tablet estreito), vira barra so com icones

class Sidebar(ft.Container):
    def __init__(self, page: ft.Page, active_route: str, on_navigate):
        super().__init__()
        self._custom_page = page
        self.active_route = active_route
        self.on_navigate = on_navigate
        self._compact = page.width is not None and page.width < COMPACT_BREAKPOINT

        # Design Premium do Painel Lateral
        self.width = 76 if self._compact else 260
        self.bgcolor = ft.Colors.SURFACE
        self.border = ft.Border(right=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT))
        self.padding = ft.Padding.only(top=30, left=10 if self._compact else 15, right=10 if self._compact else 15, bottom=20)

        self.content = self._build_content()

    @property
    def page(self):
        return self._custom_page

    def set_compact(self, compact: bool) -> None:
        """Alterna entre a barra lateral completa e a versão compacta (só ícones),
        chamado ao redimensionar a janela/navegador (ver page.on_resize em app.py)."""
        if compact == self._compact:
            return
        self._compact = compact
        self.width = 76 if compact else 260
        self.padding = ft.Padding.only(top=30, left=10 if compact else 15, right=10 if compact else 15, bottom=20)
        self.content = self._build_content()
        try:
            self.update()
        except RuntimeError:
            pass

    def _build_content(self) -> ft.Control:
        # Título da Marca (Brand Header) -- só o ícone quando compacto
        if self._compact:
            brand_header = ft.Container(
                content=ft.Icon(ft.Icons.MONETIZATION_ON_OUTLINED, color=ft.Colors.BLUE_400, size=28),
                alignment=ft.Alignment.CENTER,
                margin=ft.Margin.only(bottom=24),
                tooltip="PATRIMÔNIO - Controle Interno"
            )
        else:
            brand_header = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.MONETIZATION_ON_OUTLINED, color=ft.Colors.BLUE_400, size=30),
                    ft.Column([
                        ft.Text("PATRIMÔNIO", size=16, weight=ft.FontWeight.BOLD, style=ft.TextStyle(letter_spacing=1.5)),
                        ft.Text("Controle Interno", size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                    ], spacing=1),
                ], alignment=ft.MainAxisAlignment.START),
                margin=ft.Margin.only(bottom=30, left=10)
            )

        # Itens do Menu
        menu_items = [
            ("Dashboard", ft.Icons.DASHBOARD_ROUNDED, "/dashboard"),
            ("Patrimônios", ft.Icons.INVENTORY_ROUNDED, "/assets"),
            ("Manutenções", ft.Icons.BUILD_ROUNDED, "/maintenances"),
            ("Funcionários", ft.Icons.PEOPLE_ALT_ROUNDED, "/employees"),
            ("Categorias", ft.Icons.CATEGORY_ROUNDED, "/categories"),
            ("Setores", ft.Icons.BUSINESS_CENTER_ROUNDED, "/sectors"),
        ]

        menu_column = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
        for label, icon, route in menu_items:
            menu_column.controls.append(self._build_menu_item(label, icon, route))

        # Alternador de Tema (Claro/Escuro)
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        if self._compact:
            theme_toggle = ft.Container(
                content=ft.IconButton(
                    ft.Icons.DARK_MODE_ROUNDED if is_dark else ft.Icons.LIGHT_MODE_ROUNDED,
                    icon_color=ft.Colors.BLUE_200 if is_dark else ft.Colors.AMBER,
                    tooltip="Alternar modo escuro/claro",
                    on_click=self._toggle_theme_compact
                ),
                alignment=ft.Alignment.CENTER,
                margin=ft.Margin.only(top=20)
            )
        else:
            theme_toggle = ft.Container(
                content=ft.Row([
                    ft.Icon(
                        ft.Icons.DARK_MODE_ROUNDED if is_dark else ft.Icons.LIGHT_MODE_ROUNDED,
                        color=ft.Colors.AMBER if not is_dark else ft.Colors.BLUE_200,
                        size=20
                    ),
                    ft.Text(
                        "Modo Escuro" if is_dark else "Modo Claro",
                        size=13,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Switch(
                        value=is_dark,
                        on_change=self._toggle_theme,
                        active_color=ft.Colors.BLUE_400
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.Padding.all(12),
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                border_radius=10,
                margin=ft.Margin.only(top=20)
            )

        return ft.Column([
            brand_header,
            ft.Container(content=menu_column, expand=True),
            theme_toggle
        ], expand=True)

    def _build_menu_item(self, label: str, icon: str, route: str) -> ft.Container:
        is_active = self.active_route == route

        # Estilização do Item Ativo vs Inativo
        bg_color = ft.Colors.BLUE_900 if is_active else ft.Colors.TRANSPARENT
        icon_color = ft.Colors.BLUE_200 if is_active else ft.Colors.ON_SURFACE_VARIANT
        text_color = ft.Colors.BLUE_100 if is_active else ft.Colors.ON_SURFACE
        font_weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500

        if self._compact:
            content = ft.Icon(icon, color=icon_color, size=22)
        else:
            content = ft.Row([
                ft.Icon(icon, color=icon_color, size=20),
                ft.Text(label, color=text_color, size=14, weight=font_weight),
            ], spacing=12)

        item = ft.Container(
            content=content,
            padding=ft.Padding.symmetric(vertical=14 if self._compact else 12, horizontal=8 if self._compact else 16),
            bgcolor=bg_color,
            border_radius=8,
            alignment=ft.Alignment.CENTER if self._compact else None,
            tooltip=label if self._compact else None,
            on_click=lambda e: self.on_navigate(route),
            on_hover=lambda e: self._on_item_hover(e, is_active)
        )
        return item

    def _on_item_hover(self, e: ft.HoverEvent, is_active: bool) -> None:
        # Efeito de hover (micro-animação de fundo)
        if not is_active:
            e.control.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGH if e.data == "true" else ft.Colors.TRANSPARENT
            e.control.update()

    def _toggle_theme_compact(self, e) -> None:
        self._toggle_theme(None)

    def _toggle_theme(self, e) -> None:
        # Alterna o tema da página inteira de forma reativa
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
        self.page.update()

        # Recarrega a sidebar para atualizar o switch do tema
        self.content = self._build_content()
        self.update()
