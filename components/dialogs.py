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

def show_open_link_snackbar(page: ft.Page, message: str, url: str):
    """
    Exibe uma mensagem com um link clicável pra abrir um arquivo na web.

    Não abre a URL sozinho -- navegadores bloqueiam popups/abas abertas fora
    de um clique direto do usuário (e essa chamada acontece depois de uma
    ida-e-volta assíncrona ao servidor, então não conta como clique direto).
    O botão "Abrir" é um link de verdade (atributo `url` do TextButton), então
    o clique nele é reconhecido como ação do usuário e não é bloqueado.
    """
    if not page:
        return
    snack = ft.SnackBar(
        content=ft.Row(
            [
                ft.Text(message, color=ft.Colors.WHITE),
                ft.TextButton(
                    "Abrir",
                    url=url,
                    style=ft.ButtonStyle(color=ft.Colors.WHITE),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=ft.Colors.GREEN_700,
        behavior=ft.SnackBarBehavior.FLOATING,
        dismiss_direction=ft.DismissDirection.DOWN,
        duration=ft.Duration(seconds=10),
        open=True
    )
    if snack not in page.overlay:
        page.overlay.append(snack)
    page.snack_bar = snack
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
