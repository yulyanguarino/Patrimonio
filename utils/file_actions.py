import os
from pathlib import Path

import flet as ft

from config.settings import BASE_DIR

_ASSETS_DIR = (BASE_DIR / "assets").resolve()


def open_file(page: ft.Page, path: str) -> bool:
    """
    Abre um arquivo pro usuário ver.

    No desktop, abre com o programa padrão do sistema operacional. Na web,
    não há acesso ao disco do usuário -- abre numa nova aba a URL pública do
    arquivo (servida em /assets/..., já que labels/anexos ficam dentro da
    pasta "assets"). Retorna False se o arquivo não puder ser aberto.
    """
    if not path or not os.path.exists(path):
        return False

    if page.web:
        try:
            rel = Path(path).resolve().relative_to(_ASSETS_DIR)
        except ValueError:
            return False
        page.launch_url(f"/assets/{rel.as_posix()}")
        return True

    os.startfile(path)
    return True
