import flet as ft
from app import PatrimonioApp

def main(page: ft.Page):
    # Configurações de dimensão e título da janela desktop
    page.title = "Sistema de Controle Patrimonial"
    page.window.width = 1280
    page.window.height = 800
    page.window.min_width = 1000
    page.window.min_height = 650

    # Define o tema escuro padrão para estética premium
    page.theme_mode = ft.ThemeMode.DARK

    # Instancia a aplicação patrimonial
    app = PatrimonioApp(page)

    # Gerenciador de fechamento seguro para liberar a conexão com o PostgreSQL
    def on_window_event(e):
        if e.data == "close":
            app.close()
            page.window.destroy()

    page.window.prevent_close = True
    page.window.on_event = on_window_event

    # Adiciona o componente mestre à página
    page.add(app)

if __name__ == "__main__":
    # Inicializa o aplicativo desktop Flet
    ft.run(main)
