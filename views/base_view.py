import flet as ft

class BaseView(ft.Container):
    """
    Classe base para todas as telas (Views) do sistema.
    Garante uniformidade visual e define o ciclo de vida (on_mount) para carregamento reativo.
    """
    def __init__(self, page: ft.Page, controller=None, **kwargs):
        super().__init__(**kwargs)
        self._custom_page = page
        self.controller = controller
        self.expand = True
        self.padding = ft.Padding.all(24)
        
        # Cores e design responsivo padrão
        self.bgcolor = ft.Colors.SURFACE

    @property
    def page(self):
        return self._custom_page

    def on_mount(self) -> None:
        """
        Método de ciclo de vida invocado sempre que a tela é montada e exibida na UI.
        Usado para carregar dados dos repositórios e atualizar dropdowns/tabelas.
        """
        pass
