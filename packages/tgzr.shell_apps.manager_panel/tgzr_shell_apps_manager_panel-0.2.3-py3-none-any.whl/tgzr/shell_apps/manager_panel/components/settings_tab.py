from nicegui import ui

from tgzr.nice.data_elements.contextual_settings_view import ContextualSettingsView

from .state import State


async def settings_tab(state: State):
    if state.session is None:
        ui.label("No active session. Please login.")
        return
    if state.session.workspace is None:
        ui.label("No valid session. Please login.")
        return

    view = ContextualSettingsView(
        state.settings_context or [],
        state.session,
        state.visid,
        history_closed=False,
        auto_expand_groups=state.settings.settings_tab.auto_expand_groups,
    ).classes("w-full")
    view.render()
