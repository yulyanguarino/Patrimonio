"""Gera o HTML da página de status do patrimônio (aberta ao escanear o QR Code).

Compartilhado entre o servidor local do modo desktop (web/status_server.py)
e a rota pública exposta quando o app roda hospedado (web_main.py).
"""
from services.inventory_import_service import INVENTORY_CATEGORIES

STATUS_COLORS = {
    "Disponível": "#4CAF50",
    "Em uso": "#2196F3",
    "Em manutenção": "#FFC107",
    "Baixado": "#F44336",
}


def render_not_found_html() -> str:
    return "<h1>404 - Patrimônio não encontrado</h1>"


def render_asset_status_html(asset) -> str:
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
.tech{{white-space:pre-line;font-size:13px;line-height:1.6}}
</style></head><body>
<h1>[{asset.numero_patrimonial}] {asset.nome}</h1>
<span class="badge">{asset.status}</span>
<div class="card">
<p><b>Categoria:</b> {asset.category.nome if asset.category else '-'}</p>
<p><b>Setor:</b> {asset.sector.nome if asset.sector else '-'}</p>
<p><b>Responsável:</b> {asset.employee.nome if asset.employee else 'Nenhum'}</p>
<p><b>Última atualização:</b> {atualizado}</p>
</div>
{_render_technical_info_html(asset)}
<h2>Histórico de Manutenções</h2>
{_render_maintenances_html(asset.maintenances)}
</body></html>"""


def _render_technical_info_html(asset) -> str:
    category_name = asset.category.nome if asset.category else None
    if category_name not in INVENTORY_CATEGORIES or not asset.observacoes:
        return ""
    return f"""<h2>Informações Técnicas</h2>
<div class="card"><p class="tech">{asset.observacoes}</p></div>"""


def _render_maintenances_html(maintenances) -> str:
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
