import io
import os

import qrcode
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from config.settings import LABELS_DIR, LOCAL_SERVER_PORT
from repositories.asset_repository import AssetRepository
from utils.exceptions import BusinessRuleException
from utils.network import get_local_ip

# --- Layout da etiqueta térmica (tamanho confirmado: rolo real medido em 5x3cm, impressora Elgin L42) ---
# Estrutura inspirada na etiqueta de referência do usuário: QR Code à esquerda (no lugar do
# código de barras), texto "PATRIMÔNIO" + número em destaque à direita. O arranjo em 2 colunas
# na impressão fica a cargo do utilitário da Elgin -- aqui só geramos cada etiqueta individual.
LABEL_WIDTH_MM = 50
LABEL_HEIGHT_MM = 30
LABEL_MARGIN_MM = 3
QR_SIZE_MM = 22
FONT_SIZE_LABEL = 8
FONT_SIZE_NUMERO = 14


class LabelService:
    def __init__(self, db: Session):
        self.db = db
        self.asset_repo = AssetRepository(db)

    def generate_label(self, asset_id: int) -> str:
        """Gera o PDF de etiqueta de um único patrimônio (comportamento original, inalterado)."""
        asset = self.asset_repo.get_by_id(asset_id)
        if not asset:
            raise BusinessRuleException("Patrimônio não encontrado.")

        output_path = LABELS_DIR / f"{asset.numero_patrimonial}_etiqueta.pdf"
        c = canvas.Canvas(str(output_path), pagesize=(LABEL_WIDTH_MM * mm, LABEL_HEIGHT_MM * mm))
        self._draw_label(c, asset)
        c.save()
        return str(output_path)

    def generate_labels_bulk(self, asset_ids: list[int]) -> str:
        """Gera um único PDF com uma etiqueta por página, para imprimir vários de uma vez."""
        assets = [self.asset_repo.get_by_id(asset_id) for asset_id in asset_ids]
        assets = [a for a in assets if a]
        if not assets:
            raise BusinessRuleException("Nenhum patrimônio encontrado para gerar etiquetas.")

        output_path = LABELS_DIR / "etiquetas_lote.pdf"
        c = canvas.Canvas(str(output_path), pagesize=(LABEL_WIDTH_MM * mm, LABEL_HEIGHT_MM * mm))
        for asset in assets:
            self._draw_label(c, asset)
        c.save()
        return str(output_path)

    def _draw_label(self, c: canvas.Canvas, asset) -> None:
        """Desenha uma etiqueta na página atual do canvas e fecha a página (showPage)."""
        url = self._build_status_url(asset.numero_patrimonial)
        qr_img = qrcode.make(url, box_size=10, border=1)
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        qr_reader = ImageReader(qr_buffer)
        qr_y = (LABEL_HEIGHT_MM - QR_SIZE_MM) / 2 * mm
        c.drawImage(qr_reader, LABEL_MARGIN_MM * mm, qr_y, width=QR_SIZE_MM * mm, height=QR_SIZE_MM * mm)

        text_x = (LABEL_MARGIN_MM * 2 + QR_SIZE_MM) * mm
        c.setFont("Helvetica-Bold", FONT_SIZE_LABEL)
        c.drawString(text_x, (LABEL_HEIGHT_MM - 8) * mm, "PATRIMÔNIO")

        c.setFont("Helvetica-Bold", FONT_SIZE_NUMERO)
        c.drawString(text_x, (LABEL_HEIGHT_MM - 16) * mm, asset.numero_patrimonial)

        c.showPage()

    def _build_status_url(self, numero_patrimonial: str) -> str:
        public_base_url = os.getenv("PUBLIC_BASE_URL")
        if public_base_url:
            return f"{public_base_url.rstrip('/')}/patrimonio/{numero_patrimonial}"
        ip = get_local_ip()
        return f"http://{ip}:{LOCAL_SERVER_PORT}/patrimonio/{numero_patrimonial}"
