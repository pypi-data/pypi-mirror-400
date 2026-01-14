from nicegui import ui, run


async def message_dialog(button: str | None = "Ok", big: bool = False):
    with ui.dialog() as dialog, ui.card() as card:
        if big:
            card.classes("min-w-[80vw] min-h-[80vh]")
        # dialog.props('backdrop-filter="brightness(30%) blur(5px) "')
        content = ui.column().classes("w-full")
        with ui.row().classes("w-full"):
            ui.space()
            if button:
                ui.button(button, on_click=dialog.close)
    content.dialog = dialog  # type: ignore 🫣
    yield content
    await dialog
    dialog.clear()


async def async_call_with_progress(f, *args):
    with ui.dialog() as dialog, ui.card():
        ui.spinner(size="lg")
    dialog.open()
    try:
        result = await run.cpu_bound(f, *args)
    finally:
        dialog.close()
    return result
