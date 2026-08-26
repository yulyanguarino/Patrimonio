import os
from pathlib import Path
from typing import Optional

import flet as ft

from config.settings import BASE_DIR
from components.dialogs import show_success_snackbar, show_open_link_snackbar

_ASSETS_DIR = (BASE_DIR / "assets").resolve()


def _get_file_url(path: str) -> Optional[str]:
    """URL pública (/assets/...) de um arquivo salvo dentro da pasta assets/, ou None."""
    try:
        rel = Path(path).resolve().relative_to(_ASSETS_DIR)
    except ValueError:
        return None
    return f"/assets/{rel.as_posix()}"


async def reveal_file(
    page: ft.Page,
    path: str,
    desktop_message: Optional[str] = None,
    web_message: str = "Arquivo pronto!",
) -> bool:
    """
    Mostra pro usuário o resultado de uma operação de arquivo (etiqueta gerada,
    anexo aberto).

    No desktop, abre direto com o programa padrão do sistema operacional. Na
    web não dá pra abrir sozinho (bloqueio de popup do navegador, já que não
    é resultado de um clique direto) -- em vez disso mostra uma mensagem com
    um link clicável de verdade. Retorna False se o arquivo não existir ou
    (na web) não estiver dentro da pasta assets/ (a única servida publicamente).
    """
    if not path or not os.path.exists(path):
        return False

    if page.web:
        url = _get_file_url(path)
        if not url:
            return False
        show_open_link_snackbar(page, web_message, url)
    else:
        if desktop_message:
            show_success_snackbar(page, desktop_message)
        os.startfile(path)

    return True
