import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import flet as ft

from config.settings import BASE_DIR
from components.dialogs import show_success_snackbar, show_open_link_dialog

_ASSETS_DIR = (BASE_DIR / "assets").resolve()


_WS_TO_HTTP_SCHEME = {"wss": "https", "ws": "http"}


def _get_file_url(page: ft.Page, path: str) -> Optional[str]:
    """URL pública absoluta de um arquivo salvo dentro da pasta assets/, ou None."""
    try:
        rel = Path(path).resolve().relative_to(_ASSETS_DIR)
    except ValueError:
        return None

    public_base_url = os.getenv("PUBLIC_BASE_URL")
    if public_base_url:
        return f"{public_base_url.rstrip('/')}/assets/{rel.as_posix()}"

    # Sem PUBLIC_BASE_URL configurado: monta a partir de page.url. Em apps
    # Flet web, page.url reflete o endpoint de WebSocket (wss://) usado pela
    # conexão da sessão, não a URL http(s) real da página -- por isso troca
    # o esquema antes de usar, senão o navegador recusa (ERR_UNKNOWN_URL_SCHEME).
    origin = urlparse(page.url or "")
    scheme = _WS_TO_HTTP_SCHEME.get(origin.scheme, origin.scheme)
    if scheme and origin.netloc:
        return f"{scheme}://{origin.netloc}/assets/{rel.as_posix()}"
    return f"/assets/{rel.as_posix()}"


async def reveal_file(
    page: ft.Page,
    path: str,
    desktop_message: Optional[str] = None,
    web_title: str = "Arquivo pronto!",
) -> bool:
    """
    Mostra pro usuário o resultado de uma operação de arquivo (etiqueta gerada,
    anexo aberto).

    No desktop, abre direto com o programa padrão do sistema operacional. Na
    web, mostra um modal com o link pra copiar (ver show_open_link_dialog --
    tentar abrir automaticamente não é confiável nessa versão do Flet).
    Retorna False se o arquivo não existir ou (na web) não estiver dentro da
    pasta assets/ (a única servida publicamente).
    """
    if not path or not os.path.exists(path):
        return False

    if page.web:
        url = _get_file_url(page, path)
        if not url:
            return False
        show_open_link_dialog(page, web_title, url)
    else:
        if desktop_message:
            show_success_snackbar(page, desktop_message)
        os.startfile(path)

    return True
