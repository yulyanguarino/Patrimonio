import flet as ft

class StatCard(ft.Container):
    def __init__(self, title: str, value: str, icon: str, icon_color: str, **kwargs):
        super().__init__(**kwargs)
        
        self.value_display = ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
        
        # Design Premium (Glassmorphism / Bordered Card)
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_LOW
        self.border = ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
        self.border_radius = 12
        self.padding = ft.Padding.all(20)
        self.expand = True
        
        self.content = ft.Row([
            ft.Column([
                ft.Text(title, size=13, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500),
                self.value_display,
            ], spacing=4, expand=True),
            ft.Container(
                content=ft.Icon(icon, color=icon_color, size=30),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                padding=12,
                border_radius=10
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def update_value(self, new_value: str) -> None:
        """Atualiza o valor exibido no card de estatística."""
        self.value_display.value = new_value
        try:
            self.value_display.update()
        except RuntimeError:
            pass
