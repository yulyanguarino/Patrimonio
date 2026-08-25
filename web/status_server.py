import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from config.database import SessionLocal
from config.settings import LOCAL_SERVER_HOST, LOCAL_SERVER_PORT
from repositories.asset_repository import AssetRepository
from web.status_page import render_asset_status_html, render_not_found_html

_httpd = None
_thread = None


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
            self._write_html(200, render_asset_status_html(asset))
        finally:
            db.close()

    def _serve_404(self):
        self._write_html(404, render_not_found_html())

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
