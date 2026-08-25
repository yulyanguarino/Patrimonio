"""
Ponto de entrada usado SÓ para empacotar o .exe de demonstração (flet pack).

Não é usado no dia a dia -- `python main.py` continua funcionando pra sempre,
sem expiração. Isso aqui só existe pra travar a versão .exe que sai da sua
máquina, evitando que ela continue sendo usada depois da apresentação.

Pra renovar/gerar uma nova demo, é só pedir -- ajusto a data e reempacoto.
"""
from datetime import datetime

import flet as ft

from main import main as real_main

DEMO_EXPIRES_AT = datetime(2026, 8, 27, 18, 0)


def demo_main(page: ft.Page):
    if datetime.now() > DEMO_EXPIRES_AT:
        page.title = "Sistema de Controle Patrimonial"
        page.theme_mode = ft.ThemeMode.DARK
        page.window.width = 460
        page.window.height = 220
        page.window.prevent_close = False
        page.add(
            ft.Column(
                [
                    ft.Text("Versão de demonstração expirada", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Entre em contato para renovar o acesso.",
                        size=14,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )
        return

    real_main(page)


if __name__ == "__main__":
    ft.run(demo_main)
