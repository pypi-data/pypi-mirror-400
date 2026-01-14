from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass


if TYPE_CHECKING:
    from tgzr.nice.tgzr_visid import TGZRVisId

    from tgzr.shell.session import Session
    from tgzr.shell.studio import Studio
    from tgzr.shell.project import Project

    from ..app import ManagerPanelSettings


@dataclass
class State:
    visid: TGZRVisId
    settings: ManagerPanelSettings
    session: Session | None = None
    studio: Studio | None = None
    project: Project | None = None
    package_name: str | None = None
    settings_context: list[str] | None = None
