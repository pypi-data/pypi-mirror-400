from collections import defaultdict

from nicegui import ui

from tgzr.shell.app_sdk._base_app import _BaseShellApp, ShellAppContext, ShellAppInfo

from .state import State


def get_grouped_apps_info(
    context: ShellAppContext,
    apps: list[_BaseShellApp],
) -> list[tuple[str, list[ShellAppInfo]]]:
    groups = defaultdict(list)
    all: dict[str, ShellAppInfo] = {}
    for app in apps:
        for group in app.app_groups:
            if group.startswith("_"):
                continue
            app_info = app.get_info(context)
            if not app_info.hidden:
                all[app_info.app_id] = app_info
                groups[group].append(app_info)
    return [("all", list(all.values()))] + sorted(groups.items())


def render_apps_buttons(
    grouped_apps_info: list[tuple[str, list[ShellAppInfo]]],
    default_icon: str | None = None,
    default_color: str | None = None,
):
    with ui.column(align_items="center").classes("w-full h-full gap-0") as c:
        with ui.tabs() as tabs:
            for group, apps_info in grouped_apps_info:
                ui.tab(group, label=group.replace("_", " ").title())
        with ui.tab_panels(tabs).classes("w-full h-full") as tps:
            for group, apps_info in grouped_apps_info:
                with ui.tab_panel(group) as tp:
                    if group == "all":
                        tabs.set_value(tp)
                    with ui.row().classes("w-full xh-full row wrap justify-center"):
                        for app_info in apps_info:
                            icon = app_info.icon or default_icon
                            color = app_info.color or default_color
                            if 1:
                                # TODO: manage this kind of value in preferences
                                if 0:
                                    pref_with_label = False
                                    pref_size = "xl"
                                    pref_round = "round"
                                    pref_push = "push"
                                else:
                                    pref_with_label = True
                                    pref_size = "md"
                                    pref_round = "rounded"
                                    pref_push = ""
                                pref_props = f'{pref_round} {pref_push} xoutline size="{pref_size}"'
                                pref_classes = "glossy"
                                pref_classes = ""
                            ui.button(
                                pref_with_label and app_info.title or "",
                                icon=icon,
                                color=color,
                                on_click=lambda e, app_info=app_info: app_info.run_app(
                                    notify=ui.notify
                                ),
                            ).props(pref_props).classes(pref_classes).tooltip(
                                app_info.title
                            )


async def apps_tab(state: State):
    if state.session is None:
        ui.label("No active session. Please login.")
        return
    if state.session.workspace is None:
        ui.label("No valid session. Please login.")
        return

    app_host_name = "tgzr.shell_apps.manager_panel.apps_tab:hosts"

    @ui.refreshable
    async def main_layout():
        if state.session is None:
            ui.label("No active session. Please login.")
            return

        apps = state.session.apps()

        with ui.row().classes("w-full h-full gap-0"):
            with ui.column(align_items="center").classes("w-1/2 h-full"):
                context = ShellAppContext(
                    session=state.session,
                    host_name=app_host_name,
                    context_name="_HOST_",
                )
                host_app_groups = get_grouped_apps_info(context, apps)
                host_app_groups = [(g, l) for g, l in host_app_groups if g != "host"]
                render_apps_buttons(
                    host_app_groups,
                    default_icon="sym_o_design_services",
                    default_color="positive",
                )
            with ui.column(align_items="center").classes("w-1/2 h-full"):
                context = ShellAppContext(
                    session=state.session, host_name=app_host_name, context_name="_EXE_"
                )
                app_groups = get_grouped_apps_info(context, apps)
                render_apps_buttons(
                    app_groups,
                    default_icon="sym_o_diamond",
                    default_color="primary",
                )

        return

    await main_layout()
