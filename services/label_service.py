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

# --- Comandos ZPL (impressora Elgin L42 Pro, 203 DPI de fábrica -- se a sua
# unidade foi atualizada pra 300 DPI, mude ZPL_DPI pra 300) ---
# Ainda não testado numa impressora de verdade -- provavelmente precisa de um
# ajuste fino de posição/tamanho depois do primeiro teste real na aba
# "Comandos" do L42 Pro Utility.
ZPL_DPI = 203
ZPL_QR_MAGNIFICATION = 5  # fator de escala do QR (1-10) -- ajustar se sair grande/pequeno demais


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

    def generate_label_zpl(self, asset_id: int) -> str:
        """Gera um arquivo .txt com o comando ZPL de um único patrimônio, pra
        carregar direto na aba "Comandos" do L42 Pro Utility e enviar pra
        impressora (sem passar por PDF). O rolo é fisicamente 2 colunas por
        fileira, então a etiqueta é repetida nas duas colunas da mesma
        fileira (senão a impressora avança a fileira toda mesmo imprimindo
        só uma etiqueta, desperdiçando a outra coluna)."""
        asset = self.asset_repo.get_by_id(asset_id)
        if not asset:
            raise BusinessRuleException("Patrimônio não encontrado.")

        output_path = LABELS_DIR / f"{asset.numero_patrimonial}_etiqueta.txt"
        zpl = self._build_zpl_row(asset, asset)
        output_path.write_text(zpl, encoding="utf-8")
        return str(output_path)

    def generate_labels_bulk_zpl(self, asset_ids: list[int]) -> str:
        """Gera um único arquivo .txt com um bloco ZPL por fileira do rolo
        (2 etiquetas lado a lado, igual ao PDF de 2 colunas) -- se sobrar
        uma etiqueta ímpar na última fileira, repete a última pra não
        deixar a coluna em branco."""
        assets = [self.asset_repo.get_by_id(asset_id) for asset_id in asset_ids]
        assets = [a for a in assets if a]
        if not assets:
            raise BusinessRuleException("Nenhum patrimônio encontrado para gerar etiquetas.")

        blocks = []
        for i in range(0, len(assets), 2):
            left_asset = assets[i]
            right_asset = assets[i + 1] if i + 1 < len(assets) else left_asset
            blocks.append(self._build_zpl_row(left_asset, right_asset))

        output_path = LABELS_DIR / "etiquetas_lote.txt"
        output_path.write_text("".join(blocks), encoding="utf-8")
        return str(output_path)

    def _mm_to_dots(self, value_mm: float) -> int:
        return round(value_mm * ZPL_DPI / 25.4)

    def _build_zpl_row(self, left_asset, right_asset) -> str:
        """Monta o bloco ZPL (^XA...^XZ) de UMA FILEIRA do rolo -- 2
        etiquetas lado a lado (esquerda/direita), reproduzindo em dots o
        mesmo layout físico usado no PDF de 2 colunas
        (_generate_bulk_two_columns/_draw_label): borda do rolo, gap entre
        colunas, QR à esquerda de cada etiqueta e "PATRIMÔNIO" + número à
        direita."""
        row_width_dots = self._mm_to_dots(2 * LABEL_WIDTH_MM + ROLL_COLUMN_GAP_MM + 2 * ROLL_BORDER_MM)
        height_dots = self._mm_to_dots(LABEL_HEIGHT_MM)

        left_offset_mm = ROLL_BORDER_MM
        right_offset_mm = ROLL_BORDER_MM + LABEL_WIDTH_MM + ROLL_COLUMN_GAP_MM

        fields = "".join(
            self._build_zpl_fields(asset, offset_mm, height_dots)
            for asset, offset_mm in ((left_asset, left_offset_mm), (right_asset, right_offset_mm))
        )

        return (
            "^XA\n"
            f"^PW{row_width_dots}\n"
            f"^LL{height_dots}\n"
            f"{fields}"
            "^PQ1\n"
            "^XZ\n"
        )

    def _build_zpl_fields(self, asset, offset_mm: float, height_dots: int) -> str:
        """Campos (QR + texto) de uma etiqueta dentro da fileira, a partir de offset_mm."""
        url = self._build_status_url(asset.numero_patrimonial)

        offset_dots = self._mm_to_dots(offset_mm)
        margin_dots = self._mm_to_dots(LABEL_MARGIN_MM)
        qr_size_dots = self._mm_to_dots(QR_SIZE_MM)

        qr_x = offset_dots + margin_dots
        qr_y = (height_dots - qr_size_dots) // 2
        text_x = offset_dots + margin_dots * 2 + qr_size_dots

        return (
            f"^FO{qr_x},{qr_y}^BQN,2,{ZPL_QR_MAGNIFICATION}^FDQA,{url}^FS\n"
            f"^FO{text_x},{margin_dots}^A0N,24,24^FDPATRIMONIO^FS\n"
            f"^FO{text_x},{margin_dots + 34}^A0N,40,40^FD{asset.numero_patrimonial}^FS\n"
        )

    def _build_status_url(self, numero_patrimonial: str) -> str:
        public_base_url = os.getenv("PUBLIC_BASE_URL")
        if public_base_url:
            return f"{public_base_url.rstrip('/')}/patrimonio/{numero_patrimonial}"
        ip = get_local_ip()
        return f"http://{ip}:{LOCAL_SERVER_PORT}/patrimonio/{numero_patrimonial}"
