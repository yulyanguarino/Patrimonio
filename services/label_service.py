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
# código de barras), texto "PATRIMÔNIO" + número em destaque à direita.
LABEL_WIDTH_MM = 50
LABEL_HEIGHT_MM = 30
LABEL_MARGIN_MM = 3
QR_SIZE_MM = 22
FONT_SIZE_LABEL = 8
FONT_SIZE_NUMERO = 14

# Medidas do rolo físico (2 colunas lado a lado) confirmadas pelo usuário --
# usadas só na geração em lote com 2 colunas (services/label_service.py::generate_labels_bulk).
ROLL_BORDER_MM = 4      # 0,4cm de borda nas laterais do rolo
ROLL_COLUMN_GAP_MM = 3  # 0,3cm de espaço entre as duas etiquetas lado a lado


class LabelService:
    def __init__(self, db: Session):
        self.db = db
        self.asset_repo = AssetRepository(db)

    def generate_label(self, asset_id: int) -> str:
        """Gera o PDF de etiqueta de um único patrimônio (1 etiqueta, 1 página)."""
        asset = self.asset_repo.get_by_id(asset_id)
        if not asset:
            raise BusinessRuleException("Patrimônio não encontrado.")

        output_path = LABELS_DIR / f"{asset.numero_patrimonial}_etiqueta.pdf"
        c = canvas.Canvas(str(output_path), pagesize=(LABEL_WIDTH_MM * mm, LABEL_HEIGHT_MM * mm))
        self._draw_label(c, asset)
        c.showPage()
        c.save()
        return str(output_path)

    def generate_labels_bulk(self, asset_ids: list[int], columns: int = 1) -> str:
        """
        Gera um único PDF com as etiquetas de vários patrimônios, uma fileira
        por página. Com columns=1, cada página tem 1 etiqueta (como antes).
        Com columns=2, cada página tem 2 etiquetas lado a lado, imitando o
        rolo físico (2 colunas) -- se sobrar uma etiqueta ímpar na última
        fileira, repete a última pra não deixar a coluna em branco.
        """
        assets = [self.asset_repo.get_by_id(asset_id) for asset_id in asset_ids]
        assets = [a for a in assets if a]
        if not assets:
            raise BusinessRuleException("Nenhum patrimônio encontrado para gerar etiquetas.")

        if columns == 2:
            return self._generate_bulk_two_columns(assets)
        return self._generate_bulk_one_column(assets)

    def _generate_bulk_one_column(self, assets) -> str:
        output_path = LABELS_DIR / "etiquetas_lote.pdf"
        c = canvas.Canvas(str(output_path), pagesize=(LABEL_WIDTH_MM * mm, LABEL_HEIGHT_MM * mm))
        for asset in assets:
            self._draw_label(c, asset)
            c.showPage()
        c.save()
        return str(output_path)

    def _generate_bulk_two_columns(self, assets) -> str:
        page_width_mm = 2 * LABEL_WIDTH_MM + ROLL_COLUMN_GAP_MM + 2 * ROLL_BORDER_MM
        output_path = LABELS_DIR / "etiquetas_lote_2colunas.pdf"
        c = canvas.Canvas(str(output_path), pagesize=(page_width_mm * mm, LABEL_HEIGHT_MM * mm))

        left_offset = ROLL_BORDER_MM
        right_offset = ROLL_BORDER_MM + LABEL_WIDTH_MM + ROLL_COLUMN_GAP_MM

        for i in range(0, len(assets), 2):
            left_asset = assets[i]
            # Fileira com número ímpar de etiquetas: repete a última pra não
            # deixar a segunda coluna em branco (perdendo aquela etiqueta física).
            right_asset = assets[i + 1] if i + 1 < len(assets) else left_asset

            self._draw_label(c, left_asset, x_offset_mm=left_offset)
            self._draw_label(c, right_asset, x_offset_mm=right_offset)
            c.showPage()

        c.save()
        return str(output_path)

    def _draw_label(self, c: canvas.Canvas, asset, x_offset_mm: float = 0) -> None:
        """Desenha uma etiqueta a partir de x_offset_mm (não fecha a página)."""
        url = self._build_status_url(asset.numero_patrimonial)
        qr_img = qrcode.make(url, box_size=10, border=1)
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        qr_reader = ImageReader(qr_buffer)
        qr_y = (LABEL_HEIGHT_MM - QR_SIZE_MM) / 2 * mm
        qr_x = (x_offset_mm + LABEL_MARGIN_MM) * mm
        c.drawImage(qr_reader, qr_x, qr_y, width=QR_SIZE_MM * mm, height=QR_SIZE_MM * mm)

        text_x = (x_offset_mm + LABEL_MARGIN_MM * 2 + QR_SIZE_MM) * mm
        c.setFont("Helvetica-Bold", FONT_SIZE_LABEL)
        c.drawString(text_x, (LABEL_HEIGHT_MM - 8) * mm, "PATRIMÔNIO")

        c.setFont("Helvetica-Bold", FONT_SIZE_NUMERO)
        c.drawString(text_x, (LABEL_HEIGHT_MM - 16) * mm, asset.numero_patrimonial)

    def _build_status_url(self, numero_patrimonial: str) -> str:
        public_base_url = os.getenv("PUBLIC_BASE_URL")
        if public_base_url:
            return f"{public_base_url.rstrip('/')}/patrimonio/{numero_patrimonial}"
        ip = get_local_ip()
        return f"http://{ip}:{LOCAL_SERVER_PORT}/patrimonio/{numero_patrimonial}"
