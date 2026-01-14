from __future__ import annotations
from typing import TYPE_CHECKING, Callable

import pprint

from nicegui import ui

from tgzr.nice.tgzr_visid import TGZRVisId
from tgzr.nice.data_elements.contextual_settings_view import ContextualSettingsView

if TYPE_CHECKING:
    from tgzr.shell.session import Session
    from tgzr.shell.app_sdk._base_app import ShellAppSettings


async def render_settings(
    title: str,
    session: Session,
    visid: TGZRVisId,
    settings_context: list[str],
    settings_key: str,
    settings_model: ShellAppSettings | None = None,
):
    with ui.column(align_items="center").classes("w-full"):
        ui.label(title).classes("text-h4")

    # TODO: use the settings model to show unset/invalid keys and extended inputs
    view = ContextualSettingsView(
        settings_context,
        session,
        visid,
        scope=settings_key,
        allow_scope_change=False,
        history_closed=True,
    ).classes("w-full h-full")
    view.render()


async def settings_dialog(
    session: Session,
    visid: TGZRVisId,
    settings_context: list[str],
    settings_key: str,
    settings_model: ShellAppSettings | None = None,
    title: str = "Settings",
) -> ShellAppSettings | None:
    with ui.dialog().props("position=top") as dialog, ui.card() as card:
        card.classes("min-w-[80vw] min-h-[80vh]")
        dialog.props('backdrop-filter="brightness(30%) blur(5px) "')
        await render_settings(
            title, session, visid, settings_context, settings_key, settings_model
        )
        with ui.column(align_items="center").classes("w-full"):
            ui.button(
                icon="sym_o_top_panel_close", on_click=lambda: dialog.submit(True)
            ).tooltip("Close Settings")
    await dialog
    dialog.clear()
