import asyncio

import flet as ft

from config.settings import UPLOADS_DIR


async def resolve_picked_file(page: ft.Page, file_picker: ft.FilePicker, file) -> str:
    """
    Retorna um caminho local utilizável para um arquivo escolhido via FilePicker.

    No desktop, `file.path` já vem pronto. Na web, `file.path` é sempre `None`
    (o navegador não expõe caminhos locais) -- nesse caso, faz o upload dos
    bytes pro servidor via `file_picker.upload()` e espera terminar antes de
    devolver o caminho onde o arquivo ficou salvo.
    """
    if file.path:
        return file.path

    done = asyncio.Event()

    def on_upload(ev: ft.FilePickerUploadEvent):
        if ev.progress == 1.0 or ev.error:
            done.set()

    previous_handler = file_picker.on_upload
    file_picker.on_upload = on_upload
    try:
        upload_url = page.get_upload_url(file.name, 600)
        await file_picker.upload(
            [ft.FilePickerUploadFile(upload_url=upload_url, name=file.name)]
        )
        await done.wait()
    finally:
        file_picker.on_upload = previous_handler

    return str(UPLOADS_DIR / file.name)
