from nicegui import ui, Event, run

from tgzr.shell.session import get_default_session
from tgzr.shell.studio import Studio
from tgzr.shell.project import Project

from .state import State


def render_studio_list(state: State, on_select, create_request_event: Event):
    session = state.session
    if session is None or session.workspace is None:
        ui.label("No active session. Please login.")
        return

    default_studio_name = session.workspace.config.default_studio_name
    studios = session.workspace.get_studios()
    single = len(studios) == 1
    auto_select_studio_name = None
    if state.studio is not None:
        auto_select_studio_name = state.studio.name

    with ui.scroll_area().classes("h-full"):
        # ui.query(".q-scrollarea__content").classes("p-0")  # fuck this.
        with ui.list().props("bordered separator").classes("w-full"):
            for studio in studios:
                show_default = not single and studio.name == default_studio_name
                with ui.item(
                    on_click=lambda e, s=studio: on_select(e.sender, s)
                ) as item:
                    if auto_select_studio_name == studio.name:
                        on_select(item, studio, False)
                    with ui.item_section().props("avatar"):
                        with ui.icon(
                            "sym_o_domain", color=show_default and "primary" or None
                        ):
                            if show_default:
                                ui.tooltip("Default Studios")
                    with ui.item_section():
                        ui.item_label(studio.name)
                        ui.item_label(str(studio.path)).props("caption")
                    # if show_default:
                    #     with ui.item_section().props("side"):
                    #         ui.chip(
                    #             "default",
                    #         ).props("dense outline")
    if not studios:
        ui.button(
            "Create your first studio",
            icon="sym_o_celebration",
            on_click=lambda: create_request_event.emit(),
        ).props("flat")
    else:
        if single:
            on_select(item, studio, False)
        ui.button(
            "Create another studio",
            icon="sym_o_domain_add",
            on_click=lambda: create_request_event.emit(),
        ).props("flat")


def render_project_list(state: State, on_select, create_request_event: Event):
    studio = state.studio
    if studio is None:
        ui.label("Select a studio...")
        return
    auto_select_project_name = None
    if state.project is not None:
        auto_select_project_name = state.project.name

    default_project_name = None  # TODO: implement studio.confi.default_project_name
    project_names = studio.get_project_names()
    single = len(project_names) == 1

    with ui.scroll_area().classes("h-full"):
        # ui.query(".q-scrollarea__content").classes("p-0")  # fuck this.
        with ui.list().props("bordered separator").classes("w-full"):
            for project_name in project_names:
                project = studio.get_project(project_name)
                with ui.item(
                    on_click=lambda e, p=project: on_select(e.sender, p)
                ) as item:
                    if auto_select_project_name == project.name:
                        on_select(item, project, clear_downstream=False)
                    with ui.item_section().props("avatar"):
                        ui.icon("sym_o_theaters")
                    with ui.item_section():
                        ui.item_label(project.name)
                    with ui.item_section().props("side"):
                        if not single and studio.name == default_project_name:
                            ui.chip(
                                "default",
                            ).props("dense outline")
                        if not project.exists():
                            ui.chip("missing", color="negative").props(
                                "dense outline"
                            ).tooltip(f"Folder does not exists: {project.venv_path}")

    if not project_names:
        ui.button(
            "Create a project",
            icon="sym_o_celebration",
            on_click=lambda: create_request_event.emit(),
        ).props("flat")
    else:
        ui.button(
            "Create another project",
            icon="sym_o_video_camera_back",
            on_click=lambda: create_request_event.emit(),
        ).props("flat")


def _get_packages(
    from_object: Studio | Project,
):
    return from_object.get_packages()


async def _with_progress(f, *args):
    with ui.dialog() as dialog, ui.card():
        ui.spinner(size="lg")
    dialog.open()
    result = await run.cpu_bound(f, *args)
    dialog.close()
    return result


async def render_package_list(state: State, on_select):

    studio = state.studio
    project = state.project
    if project is None:
        if studio is None:
            with ui.column(align_items="center").classes("w-full h-full"):
                ui.label("Packages").classes("text-xl")
                ui.label("Select a studio or a project...")
            return
        dists = await _with_progress(_get_packages, studio)
    else:
        dists = await _with_progress(_get_packages, project)

    with ui.column(align_items="center").classes("w-full h-full"):
        src_indic = ""
        if studio is not None:
            src_indic += studio.name
        if project is not None:
            src_indic += ":" + project.name
        if src_indic:
            src_indic = " in " + src_indic
        ui.label(f"Packages{src_indic}").classes("text-xl")

        dists = sorted(
            dists,
            key=lambda d: (
                d.origin and "1" + d.origin.url or "2",
                "2" + d.name.lower(),
            ),
        )
        with ui.scroll_area().classes("h-full"):
            # ui.query(".q-scrollarea__content").classes("p-0")  # fuck this.
            with ui.list().props("bordered separator").classes("w-full"):
                for dist in dists:
                    package_name = dist.name
                    package_version = dist.version
                    editable_path = ""
                    if dist.origin:
                        editable_path = dist.origin.url
                    with ui.item(
                        on_click=lambda e, p=package_name: on_select(e.sender, p)
                    ):
                        col = editable_path and "orange-500" or "cyan-500"
                        with ui.item_section().props("avatar"):
                            ui.icon("sym_o_deployed_code", color=col)
                        with ui.item_section():
                            ui.item_label(package_name)
                            nb_console_scripts = len(
                                [
                                    ep
                                    for ep in dist.entry_points
                                    if ep.group == "console_scripts"
                                ]
                            )
                            nb_entry_points = (
                                len(dist.entry_points) - nb_console_scripts
                            )
                            caption = ""
                            if nb_entry_points:
                                caption = f"{nb_entry_points} Plugins"
                            ui.item_label(caption).props("caption").tooltip(
                                ", ".join([ep.group for ep in dist.entry_points])
                            )

                        with ui.item_section().props("side"):
                            with ui.row(align_items="center"):
                                ui.chip(
                                    package_version,
                                ).props("dense outline")
                                if editable_path:
                                    ui.icon("sym_o_folder", size="sm").tooltip(
                                        editable_path
                                    )
                                else:
                                    pypi_url = f"https://pypi.org/project/{package_name.split()[0]}"
                                    with ui.link(target=pypi_url, new_tab=True):
                                        ui.icon(
                                            "fa-brands fa-python", size="sm"
                                        ).tooltip(pypi_url)

    ui.button(
        "Install Package",
        icon="sym_o_install_desktop",
        on_click=lambda: ui.notify(
            "Oops, not implemented... 😅",
            position="top",
        ),
    ).props("flat")


def render_plugin_list(state: State, tgzr_only: bool, on_select):
    if state.package_name:
        tgzr_only = False

    project = state.project
    if project is None:
        studio = state.studio
        if studio is None:
            ui.label("Select a studio or a project...")
            return
        plugin_and_dist_list = studio.get_plugins(
            None, group_filter=tgzr_only and "tgzr" or None
        )
    else:
        plugin_and_dist_list = project.get_plugins(
            group_filter=tgzr_only and "tgzr" or None
        )

    plugin_and_dist_list.sort(key=lambda p: p[0].group)

    with ui.scroll_area().classes("h-full"):
        # ui.query(".q-scrollarea__content").classes("p-0")  # fuck this.
        last_group = None
        with ui.list().props("bordered").classes("w-full"):
            for entry_point, distribution in plugin_and_dist_list:
                if state.package_name and not distribution.name == state.package_name:
                    continue
                if entry_point.group != last_group:
                    if last_group is not None:
                        ui.separator()
                    ui.item_label(entry_point.group).props("header").classes(
                        "text-bold"
                    )
                last_group = entry_point.group
                with ui.item(
                    on_click=lambda e, ep=entry_point: on_select(e.sender, ep)
                ):
                    with ui.item_section().props("avatar"):
                        ui.icon("sym_o_extension")
                    with ui.item_section():
                        ui.item_label(entry_point.name)
                        ui.item_label(entry_point.value).props("caption")
                    # with ui.item_section().props("side"):
                    #     with ui.link(target="https://pypi.org/project/tgzr", new_tab=True):
                    #         ui.icon("fa-brands fa-python")


async def plugins_tab(state: State):
    if state.session is None or state.session.workspace is None:
        ui.label("No active session. Please login.")
        return

    selected_classes = "bg-teal-800"

    ui.add_css(".q-scrollarea__content{padding:0;}")  # fuck this two.

    request_studio_creation = Event()
    studio_created = Event[str]()

    request_project_creation = Event()
    project_created = Event[str]()

    def refresh_all():
        state.session = get_default_session()
        main_layout.refresh()

    with ui.dialog() as dialog, ui.card():
        ui.label("Create Dialog")

    async def on_create_studio_request():
        if state.session is None or state.session.workspace is None:
            ui.notify("Cant create a Studio: session not valid.")
            return

        dialog.clear()
        with dialog, ui.card():
            ui.label("Create Studio")
            name_input = ui.input(
                "Studio Name*",
                validation={"Needed": lambda value: value and True or False},
            )
            index_input = ui.input("Optional Index")
            find_links_input = ui.input("Optional find-links path")
            allow_prerelease_input = ui.checkbox("Allow Pre-Release")
            ui.button("Create Studio", on_click=lambda: dialog.submit(True))
        if await dialog:
            studio_name = name_input.value
            studio = state.session.workspace.get_studio(
                studio_name, ensure_exists=False
            )
            if studio.exists():
                ui.notify(
                    f"Studio {studio_name} already exists!",
                    position="top",
                    type="negative",
                )
            else:
                studio.create(
                    index=index_input.value,
                    find_links=find_links_input.value,
                    allow_prerelease=allow_prerelease_input.value,
                )
                studio_created.emit(studio_name)

    request_studio_creation.subscribe(on_create_studio_request)

    def on_studio_created(studio_name):
        refresh_all()

    studio_created.subscribe(on_studio_created)

    async def on_create_project_request():
        if state.studio is None:
            ui.notify("Select a Studio first...")
            return

        dialog.clear()
        with dialog, ui.card():
            ui.label("Create Project")
            name_input = ui.input(
                "Project Name*",
                validation={"Needed": lambda value: value and True or False},
            )
            required_packages_input = ui.input("Required Packages")
            index_input = ui.input("Optional Index")
            find_links_input = ui.input("Optional find-links path")
            allow_prerelease_input = ui.checkbox("Allow Pre-Release")
            ui.button("Create Project", on_click=lambda: dialog.submit(True))
        if await dialog:
            project_name = name_input.value
            project = state.studio.get_project(project_name)
            if project.exists():
                ui.notify(
                    f"Project {project_name} already exists!",
                    position="top",
                    type="negative",
                )
            else:
                project.create(
                    required_packages=required_packages_input.value,
                    index=index_input.value,
                    find_links=find_links_input.value,
                    allow_prerelease=allow_prerelease_input.value,
                )
                project_created.emit(project_name)

    request_project_creation.subscribe(on_create_project_request)

    def on_project_created(studio_name):
        refresh_all()

    project_created.subscribe(on_project_created)

    def on_studio_select(item: ui.item, studio: Studio, clear_downstream=True):
        if item.parent_slot is None:
            raise Exception("This should not happen.")
        for i in item.parent_slot.parent:
            i.classes(remove=selected_classes)
        item.classes(selected_classes)
        state.studio = studio
        if clear_downstream:
            state.project = None
            project_list.refresh()
            package_list.refresh()
            plugin_list.refresh()

    @ui.refreshable
    def studio_list():
        render_studio_list(state, on_studio_select, request_studio_creation)

    def on_project_select(item: ui.item, project: Project, clear_downstream=True):
        project_to_set = project
        if state.project and state.project.name == project_to_set.name:
            project_to_set = None
        if item.parent_slot is None:
            raise Exception("This should not happen.")
        for i in item.parent_slot.parent:
            i.classes(remove=selected_classes)
        if project_to_set is not None:
            item.classes(selected_classes)
        if clear_downstream:
            state.project = project_to_set
            state.package_name = None
            package_list.refresh()
            plugin_list.refresh()

    @ui.refreshable
    def project_list():
        render_project_list(state, on_project_select, request_project_creation)

    def on_package_select(item: ui.item, package_name: str):
        package_name_to_set = package_name
        if state.package_name == package_name:
            package_name_to_set = None
        if item.parent_slot is None:
            raise Exception("This should not happen.")
        for i in item.parent_slot.parent:
            i.classes(remove=selected_classes)
        if package_name_to_set:
            item.classes(selected_classes)
        state.package_name = package_name_to_set
        plugin_list.refresh()

    @ui.refreshable
    async def package_list():
        await render_package_list(state, on_package_select)

    def on_plugin_select(item: ui.item, plugin):
        # print(f"Selected Plugin: [{plugin.group}] {plugin.name}={plugin.value}")
        if item.parent_slot is None:
            raise Exception("This should not happen.")
        for i in item.parent_slot.parent:
            i.classes(remove=selected_classes)
        item.classes(selected_classes)

    @ui.refreshable
    def plugin_list(tgzr_only):
        render_plugin_list(state, tgzr_only, on_plugin_select)

    @ui.refreshable
    async def main_layout():
        with ui.row(wrap=False).classes("w-full h-full"):
            with ui.column().classes("w-full h-full"):
                with ui.column(align_items="center").classes("w-full h-full"):
                    ui.label("Studio").classes("text-xl")
                    studio_list()

            with ui.column().classes("w-full h-full"):
                with ui.column(align_items="center").classes("w-full h-full"):
                    ui.label("Project").classes("text-xl")
                    project_list()

            with ui.column().classes("w-full h-full"):
                await package_list()

            with ui.column().classes("w-full h-full"):
                with ui.column(align_items="center").classes("w-full h-full"):
                    with ui.row(align_items="center").classes("p-0"):
                        ui.label("Plugins").classes("text-xl")
                        tgzr_only_switch = (
                            ui.switch(
                                value=True,
                                on_change=lambda e: plugin_list.refresh(e.sender.value),  # type: ignore
                            )
                            .props("dense")
                            .tooltip("Only list TGZR plugins")
                        )
                    plugin_list(tgzr_only_switch.value)

    await main_layout()
