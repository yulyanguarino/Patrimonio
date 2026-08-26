"""
Ponto de entrada usado só quando o app roda hospedado (Render), via
`uvicorn web_main:app`. `main.py` continua sendo o ponto de entrada do
desktop e não é afetado por nada aqui.

Diferenças em relação ao modo desktop:
- Sem configuração de janela (não existe janela num navegador).
- Libera a conexão com o banco (db.close()) em page.on_disconnect, já que
  não existe evento de "fechar janela" na web -- cada aba/sessão fecha sua
  própria conexão quando o usuário sai ou fecha a aba.
- Expõe a rota pública /patrimonio/<numero> (fora do Flet), usada pelo QR
  Code das etiquetas -- ver LabelService/PUBLIC_BASE_URL.
"""
import os
import secrets

import flet as ft
from fastapi.responses import HTMLResponse

from app import PatrimonioApp
from config.database import SessionLocal
from repositories.asset_repository import AssetRepository
from web.status_page import render_asset_status_html, render_not_found_html

# Chave usada pelo Flet pra assinar as URLs de upload (anexos/nota fiscal).
# Se já vier definida via env var (ex: configurada no Render), usa a mesma
# em todas as instâncias/reinícios; senão, gera uma aleatória neste processo.
os.environ.setdefault("FLET_SECRET_KEY", secrets.token_hex(32))


def main(page: ft.Page):
    page.title = "Sistema de Controle Patrimonial"
    page.theme_mode = ft.ThemeMode.DARK

    patrimonio_app = PatrimonioApp(page)

    def on_disconnect(e):
        patrimonio_app.close()

    page.on_disconnect = on_disconnect
    page.add(patrimonio_app)


app = ft.run(
    main,
    view=ft.AppView.WEB_BROWSER,
    export_asgi_app=True,
    upload_dir="uploads",
)


@app.get("/patrimonio/{numero}", response_class=HTMLResponse)
def patrimonio_status(numero: str):
    db = SessionLocal()
    try:
        repo = AssetRepository(db)
        asset = repo.get_by_number(numero)
        if not asset and numero.isdigit():
            asset = repo.get_by_id(int(numero))
        if not asset:
            return HTMLResponse(render_not_found_html(), status_code=404)
        return HTMLResponse(render_asset_status_html(asset))
    finally:
        db.close()


# O Flet monta seu próprio app (Flutter shell + catch-all de rotas) na raiz "/",
# registrado antes desta rota. Como o Starlette resolve rotas na ordem em que
# foram adicionadas (não pela mais específica), essa montagem intercepta
# qualquer caminho -- incluindo /patrimonio/<numero> -- antes de chegar aqui.
# Move a rota pra frente da lista pra ela ser resolvida primeiro.
app.router.routes.insert(0, app.router.routes.pop())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
