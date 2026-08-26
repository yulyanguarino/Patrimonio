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

    # IMPORTANTE: o conteúdo de assets_dir é servido a partir da raiz do site
    # (mapeado como se fosse o próprio "/"), não sob um prefixo "/assets/"
    # como o nome sugere -- confirmado testando: <assets_dir>/labels/x.pdf
    # fica em /labels/x.pdf, e /assets/labels/x.pdf dá 404.
    url_path = rel.as_posix()

    public_base_url = os.getenv("PUBLIC_BASE_URL")
    if public_base_url:
        return f"{public_base_url.rstrip('/')}/{url_path}"

    # Sem PUBLIC_BASE_URL configurado: monta a partir de page.url. Em apps
    # Flet web, page.url reflete o endpoint de WebSocket (wss://) usado pela
    # conexão da sessão, não a URL http(s) real da página -- por isso troca
    # o esquema antes de usar, senão o navegador recusa (ERR_UNKNOWN_URL_SCHEME).
    origin = urlparse(page.url or "")
    scheme = _WS_TO_HTTP_SCHEME.get(origin.scheme, origin.scheme)
    if scheme and origin.netloc:
        return f"{scheme}://{origin.netloc}/{url_path}"
    return f"/{url_path}"


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
    web, tenta abrir automaticamente numa nova aba via page.launch_url --
    precisa ser uma URL absoluta (com https://) pra funcionar; um link
    relativo falha silenciosamente. Se não conseguir abrir sozinho (navegador
    bloquear mesmo assim), cai no modal de copiar link como alternativa.
    Retorna False se o arquivo não existir ou (na web) não estiver dentro da
    pasta assets/ (a única servida publicamente).
    """
    if not path or not os.path.exists(path):
        return False

    if page.web:
        url = _get_file_url(page, path)
        if not url:
            return False
        try:
            await page.launch_url(url)
        except Exception:
            show_open_link_dialog(page, web_title, url)
    else:
        if desktop_message:
            show_success_snackbar(page, desktop_message)
        os.startfile(path)

    return True
