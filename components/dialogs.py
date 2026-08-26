import flet as ft

def show_error_snackbar(page: ft.Page, message: str):
    """Exibe uma mensagem de erro usando SnackBar na parte inferior."""
    if not page:
        return
    snack = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.RED_700,
        behavior=ft.SnackBarBehavior.FLOATING,
        dismiss_direction=ft.DismissDirection.DOWN,
        open=True
    )
    if snack not in page.overlay:
        page.overlay.append(snack)
    page.snack_bar = snack
    try:
        page.update()
    except RuntimeError:
        pass

def show_success_snackbar(page: ft.Page, message: str):
    """Exibe uma mensagem de sucesso usando SnackBar na parte inferior."""
    if not page:
        return
    snack = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.GREEN_700,
        behavior=ft.SnackBarBehavior.FLOATING,
        dismiss_direction=ft.DismissDirection.DOWN,
        open=True
    )
    if snack not in page.overlay:
        page.overlay.append(snack)
    page.snack_bar = snack
    try:
        page.update()
    except RuntimeError:
        pass

def show_open_link_dialog(page: ft.Page, title: str, url: str):
    """
    Mostra um modal com o link de um arquivo gerado/anexado na web, pra o
    usuário copiar e abrir numa aba.

    Não tenta abrir a URL sozinho: em testes reais, tanto a abertura
    automática quanto o botão nativo de link do Flet (`url=` do TextButton,
    com ou sem `target`) fecham a aba assim que abrem -- comportamento
    inconsistente e não confiável na versão de Flet em uso. Copiar pro
    clipboard não depende de nenhuma dessas APIs de navegação, então é a
    forma confiável de entregar o link nessa versão.
    """
    if not page:
        return

    def close_dialog(e):
        dialog.open = False
        try:
            page.update()
        except RuntimeError:
            pass

    async def copy_link(e):
        await page.clipboard.set(url)
        show_success_snackbar(page, "Link copiado!")

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title, weight=ft.FontWeight.BOLD),
        content=ft.Column(
            [
                ft.Text("Copie o link abaixo e abra numa nova aba:", size=13),
                ft.TextField(value=url, read_only=True, multiline=True, min_lines=1, max_lines=3, border_radius=8),
            ],
            spacing=10,
            tight=True,
        ),
        actions=[
            ft.TextButton("Fechar", on_click=close_dialog),
            ft.ElevatedButton("Copiar Link", icon=ft.Icons.COPY_ROUNDED, on_click=copy_link, bgcolor=ft.Colors.BLUE_400, color=ft.Colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    if dialog not in page.overlay:
        page.overlay.append(dialog)
    page.dialog = dialog
    dialog.open = True
    try:
        page.update()
    except RuntimeError:
        pass

def show_confirm_dialog(page: ft.Page, title: str, message: str, on_confirm) -> ft.AlertDialog:
    """Apresenta um modal de confirmação (Sim/Não)."""
    if not page:
        return None

    def close_dialog(e):
        dialog.open = False
        try:
            page.update()
        except RuntimeError:
            pass

    def confirm_action(e):
        dialog.open = False
        try:
            page.update()
        except RuntimeError:
            pass
        on_confirm()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title, weight=ft.FontWeight.BOLD),
        content=ft.Text(message),
        actions=[
            ft.TextButton("Não", on_click=close_dialog),
            ft.ElevatedButton("Sim", on_click=confirm_action, bgcolor=ft.Colors.BLUE_400, color=ft.Colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    if dialog not in page.overlay:
        page.overlay.append(dialog)
    page.dialog = dialog
    dialog.open = True
    try:
        page.update()
    except RuntimeError:
        pass
    return dialog

def show_info_dialog(page: ft.Page, title: str, message: str) -> ft.AlertDialog:
    """Apresenta um modal informativo simples com botão de Fechar."""
    if not page:
        return None

    def close_dialog(e):
        dialog.open = False
        try:
            page.update()
        except RuntimeError:
            pass

    dialog = ft.AlertDialog(
        title=ft.Text(title, weight=ft.FontWeight.BOLD),
        content=ft.Text(message),
        actions=[
            ft.TextButton("Fechar", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    if dialog not in page.overlay:
        page.overlay.append(dialog)
    page.dialog = dialog
    dialog.open = True
    try:
        page.update()
    except RuntimeError:
        pass
    return dialog
