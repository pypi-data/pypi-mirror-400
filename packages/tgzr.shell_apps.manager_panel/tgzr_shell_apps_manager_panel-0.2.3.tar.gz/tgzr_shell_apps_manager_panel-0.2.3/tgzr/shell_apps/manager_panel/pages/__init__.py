from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Awaitable

import dataclasses

from nicegui import ui

from tgzr.nice.tgzr_visid import TGZRVisId
from tgzr.nice import layout
from tgzr.shell.session import get_default_session, set_default_session, Session
from tgzr.shell.app_sdk._base_app import ShellAppContext

from ..components.plugins_tab import plugins_tab
from ..components.apps_tab import apps_tab
from ..components.settings_tab import settings_tab
from ..components.state import State
from ..components.settings import settings_dialog

if TYPE_CHECKING:
    from ..app import ManagerPanelSettings


async def session_tab(state: State):
    session = state.session
    if session is None:
        ui.label("No session to show :/")
        return

    with ui.column(align_items="start").classes("w-full text-md tracking-wide"):
        with ui.row(align_items="center").classes("xw-full"):
            ui.label("Session Config").classes("text-h4 font-thin")
            with ui.row().classes("gap-0"):
                reload_button = (
                    ui.button(
                        icon="sym_o_restore_page",
                        on_click=lambda: update_config_fields(),
                    )
                    .tooltip("Reload")
                    .props("flat dense")
                )
                apply_btn = (
                    ui.button(
                        icon="sym_o_save",
                        on_click=lambda: ui.notify("Not implemented yet 🫣"),
                    )
                    .tooltip("Apply")
                    .props("flat dense")
                )
        with ui.column().classes("w-full"):
            verbose_cb = ui.checkbox("Verbose", value=session.config.verbose)
            home_input = ui.input("Home", value=str(session.home)).classes("w-full")

    def update_config_fields():
        verbose_cb.value = session.config.verbose
        home_input.value = str(session.home)


async def welcome_tab(state: State):
    with ui.row(align_items="start").classes("w-full h-full"):
        with ui.column(align_items="center").classes("w-full text-xl"):
            ui.label("Welcome to TGZR Manager")
            ui.label("Select a section")
            ui.label("⬅️ here")


async def install_tab(state: State):
    with ui.column(align_items="center").classes("w-full"):
        ui.button("Create new installation", icon="sym_o_location_on")
        ui.button("Duplicate this installation", icon="sym_o_moved_location")
        ui.button(
            "Remove this installation", icon="sym_o_location_off", color="negative"
        )


async def dev_tab(state: State):
    with ui.row(wrap=False).classes("w-full"):
        with ui.column(align_items="center").classes("w-full"):
            ui.label("Dev Tools").classes("text-xl")


def _add_some_settings(session, project_context, app_context, settings_context):
    from ..app import app as me

    session.settings.set_context_info(
        project_context, description="**Current Project**"
    )
    manager_panel_settings = me.get_settings(
        app_context,
        settings_context,
    )
    print("Manager Panel Settings:", manager_panel_settings)

    session.settings.set("TEST1", "LIST_KEY", ["value1"])
    session.settings.add("TEST2", "LIST_KEY", ["value2", "value3"])
    session.settings.remove("TEST3", "LIST_KEY", "value2")

    manager_panel_settings.show_install_tab = True
    me.store_settings(
        manager_panel_settings,
        app_context,
        context_name="system",
    )
    print(
        "faking settings edit +system ->",
        me.get_settings(app_context, settings_context),
    )

    manager_panel_settings.show_dev_tab = True
    me.store_settings(
        manager_panel_settings,
        app_context,
        context_name="ProjectUser",
    )
    print(
        "faking settings edit +ProjectUser ->",
        me.get_settings(app_context, settings_context),
    )

    manager_panel_settings.settings_tab.auto_expand_groups = True
    me.store_settings(
        manager_panel_settings,
        app_context,
        context_name="user",
        exclude_defaults=False,
    )
    print(
        "faking settings edit +user ->",
        me.get_settings(app_context, settings_context),
    )


@dataclasses.dataclass
class LocalState:
    current_tab_name: str | None = None
    tab_names: list[str] = dataclasses.field(default_factory=list)
    tab_renderers: dict[str, Callable[[State], Awaitable[None]]] = dataclasses.field(
        default_factory=dict
    )

    def update_from_settings(self, settings: ManagerPanelSettings):
        self.tab_names.clear()
        self.tab_renderers.clear()
        known_tabs = ["apps", "settings", "plugins", "session", "install", "dev"]
        known_renderers = dict(
            plugins=plugins_tab,
            apps=apps_tab,
            settings=settings_tab,
            session=session_tab,
            install=install_tab,
            dev=dev_tab,
        )
        if not settings.show_session_tab:
            known_tabs.remove("session")
        if not settings.show_dev_tab:
            known_tabs.remove("dev")
        if not settings.show_install_tab:
            known_tabs.remove("install")
        for tab_name in known_tabs:
            self.tab_names.append(tab_name)
            self.tab_renderers[tab_name] = known_renderers[tab_name]


@ui.page("/", title="TGZR - Manager Panel")
async def main():
    session = get_default_session()

    from ..app import app as me

    if session is None:
        raise Exception("Oops, invalid session :/")
    app_context = me.create_app_context(session)

    studio = session.get_selected_studio()
    studio_settings_context_name = studio and studio.name or "StudiosDefaults"
    project = session.get_selected_project()
    project_settings_context_name = project and project.name or "ProjectsDefaults"
    project_context = (
        f"[{studio_settings_context_name}/{project_settings_context_name}]"
    )

    settings_context = [
        "system",
        "admin",
        "user",
        project_context,
        "ProjectUser",
        "TEST1",
        "TEST2",
        "TEST3",
    ]

    ADD_SOME_SETTINGS = True  # TMP DEV: create some settings data / info
    if ADD_SOME_SETTINGS:
        _add_some_settings(
            session,
            project_context,
            app_context,
            settings_context,
        )
    manager_panel_settings = me.get_settings(app_context, settings_context)

    visid = TGZRVisId()
    state = State(
        visid=visid,
        session=session,
        settings_context=settings_context,
        settings=manager_panel_settings,
    )

    default_tab_name = None  # use welcome
    default_tab_name = "Settings"  # tmp for dev

    local_state = LocalState()
    local_state.update_from_settings(state.settings)

    # tab_renderers = dict(
    #     plugins=plugins_tab,
    #     apps=apps_tab,
    #     settings=settings_tab,
    #     install=install_tab,
    #     dev=dev_tab,
    # )

    async def change_tab(e):
        tab_name = e.value
        local_state.current_tab_name = tab_name
        await render_tab_content.refresh()

    @ui.refreshable
    async def render_tab_content():
        tab_name = local_state.current_tab_name

        renderer = None
        if tab_name is not None:
            renderer = local_state.tab_renderers.get(tab_name.lower())
        if renderer is None:
            renderer = welcome_tab

        await renderer(state)

    async def edit_settings():
        app_context = me.create_app_context(session)
        my_app_settings = me.get_settings(
            app_context,
            settings_context,
        )
        await settings_dialog(
            session, visid, settings_context, me.settings_key, my_app_settings
        )
        # re-read the settings model and update State:
        manager_panel_settings = me.get_settings(app_context, settings_context)
        state.settings = manager_panel_settings
        # update local state too:
        local_state.update_from_settings(manager_panel_settings)
        # rerender all (not only the current tab, it may have disapear)
        await render_all.refresh()

    # FIXME: this should be something like "if session not connected: connect_dialog"
    if session is None:
        await edit_settings()

    @ui.refreshable
    async def render_all():
        # manager_panel_settings = me.get_settings(app_context, settings_context)
        # state.settings = manager_panel_settings
        with layout.fullpage():
            with ui.row(align_items="center").classes("p-5 w-full"):
                visid.logo(classes="w-16")
                with ui.row(align_items="baseline"):
                    ui.label("TGZR").classes("text-5xl font-thin tracking-[1em]")
                    ui.label("Manager").classes("text-2xl font-thin tracking-[1em]")
                ui.space()
                ui.button(icon="settings", color="W", on_click=edit_settings).props(
                    "flat size=1em"
                )

            with ui.row(wrap=False).classes("w-full h-full"):
                with ui.tabs(
                    on_change=change_tab,
                ).props("vertical") as tabs:
                    for tab_name in local_state.tab_names:
                        ui.tab(tab_name)
                    tabs.set_value(local_state.current_tab_name)
                with ui.column().classes("w-full h-full p-5"):
                    await render_tab_content()

    await render_all()
