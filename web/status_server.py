import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from config.database import SessionLocal
from config.settings import LOCAL_SERVER_HOST, LOCAL_SERVER_PORT
from repositories.asset_repository import AssetRepository

_httpd = None
_thread = None

STATUS_COLORS = {
    "Disponível": "#4CAF50",
    "Em uso": "#2196F3",
    "Em manutenção": "#FFC107",
    "Baixado": "#F44336",
}


class StatusRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silencia o log padrão no stderr

    def do_GET(self):
        parts = [p for p in urlparse(self.path).path.split("/") if p]
        if len(parts) == 2 and parts[0] == "patrimonio":
            self._serve_asset_status(parts[1])
        else:
            self._serve_404()

    def _serve_asset_status(self, ident: str):
        # Sessão de banco própria e curta por requisição — nunca a sessão
        # compartilhada de longa duração usada pela GUI (app.py's self.db).
        db = SessionLocal()
        try:
            repo = AssetRepository(db)
            asset = repo.get_by_number(ident)
            if not asset and ident.isdigit():
                asset = repo.get_by_id(int(ident))
            if not asset:
                self._serve_404()
                return
            self._write_html(200, self._render_asset_html(asset))
        finally:
            db.close()

    def _render_asset_html(self, asset) -> str:
        color = STATUS_COLORS.get(asset.status, "#9E9E9E")
        atualizado = asset.atualizado_em.strftime("%d/%m/%Y %H:%M") if asset.atualizado_em else "-"
        return f"""<!DOCTYPE html>
<html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Patrimônio {asset.numero_patrimonial}</title>
<style>
body{{font-family:sans-serif;margin:0;padding:24px;background:#121212;color:#eee}}
.badge{{display:inline-block;padding:6px 14px;border-radius:6px;font-weight:bold;background:{color};color:#fff}}
.card{{background:#1e1e1e;border-radius:10px;padding:18px;margin-top:14px}}
h1{{font-size:22px;margin-bottom:4px}} p{{margin:6px 0;font-size:15px}}
h2{{font-size:16px;margin:22px 0 10px}}
.maint{{background:#1e1e1e;border-radius:10px;padding:14px;margin-top:10px}}
.maint .tipo{{display:inline-block;padding:3px 8px;border-radius:4px;font-size:11px;font-weight:bold;color:#fff}}
.tipo-corretiva{{background:#b26a00}} .tipo-preventiva{{background:#1565c0}}
.maint .data{{float:right;font-size:12px;color:#aaa}}
.empty{{font-style:italic;color:#999;font-size:14px}}
</style></head><body>
<h1>[{asset.numero_patrimonial}] {asset.nome}</h1>
<span class="badge">{asset.status}</span>
<div class="card">
<p><b>Categoria:</b> {asset.category.nome if asset.category else '-'}</p>
<p><b>Setor:</b> {asset.sector.nome if asset.sector else '-'}</p>
<p><b>Responsável:</b> {asset.employee.nome if asset.employee else 'Nenhum'}</p>
<p><b>Última atualização:</b> {atualizado}</p>
</div>
<h2>Histórico de Manutenções</h2>
{self._render_maintenances_html(asset.maintenances)}
</body></html>"""

    def _render_maintenances_html(self, maintenances) -> str:
        if not maintenances:
            return '<p class="empty">Nenhuma manutenção registrada para este patrimônio.</p>'
        sorted_maints = sorted(maintenances, key=lambda m: m.data_manutencao, reverse=True)
        cards = []
        for m in sorted_maints:
            tipo_class = "tipo-corretiva" if m.tipo == "Corretiva" else "tipo-preventiva"
            data = m.data_manutencao.strftime("%d/%m/%Y")
            proxima = f" | Próxima: {m.data_proxima.strftime('%d/%m/%Y')}" if m.data_proxima else ""
            obs = f"<p><b>Obs:</b> {m.observacoes}</p>" if m.observacoes else ""
            cards.append(f"""<div class="maint">
<span class="tipo {tipo_class}">{m.tipo.upper()}</span>
<span class="data">{data}{proxima}</span>
<p><b>Prestador:</b> {m.prestador}</p>
<p><b>Problema:</b> {m.descricao_problema}</p>
<p><b>Serviço:</b> {m.servico_executado}</p>
<p><b>Valor:</b> R$ {m.valor_gasto:,.2f}</p>
{obs}</div>""")
        return "".join(cards)

    def _serve_404(self):
        self._write_html(404, "<h1>404 - Patrimônio não encontrado</h1>")

    def _write_html(self, status: int, html: str):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start_server():
    """Sobe o servidor de status em background, se ainda não estiver rodando."""
    global _httpd, _thread
    if _httpd is not None:
        return _httpd
    try:
        _httpd = ThreadingHTTPServer((LOCAL_SERVER_HOST, LOCAL_SERVER_PORT), StatusRequestHandler)
    except OSError as e:
        print(f"[StatusServer] Falha ao iniciar na porta {LOCAL_SERVER_PORT}: {e}")
        _httpd = None
        return None
    _thread = threading.Thread(target=_httpd.serve_forever, daemon=True, name="StatusServerThread")
    _thread.start()
    print(f"[StatusServer] Ativo em http://{LOCAL_SERVER_HOST}:{LOCAL_SERVER_PORT}/patrimonio/<numero>")
    return _httpd


def stop_server():
    """Encerra o servidor de status, se estiver rodando."""
    global _httpd, _thread
    if _httpd is not None:
        _httpd.shutdown()
        _httpd.server_close()
        _httpd = None
        _thread = None
