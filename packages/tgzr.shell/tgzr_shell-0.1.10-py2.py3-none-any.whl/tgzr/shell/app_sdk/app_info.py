from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Any

import pydantic

from . import run_app_process

from ..session import Session


class ShellAppContext(pydantic.BaseModel):
    # FIXME: this should be a dataclass, no need for pydantic here.
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    session: Session
    host_name: str
    context_name: str


class DefaultShellAppInfo(pydantic.BaseModel):
    title: str | None = pydantic.Field(
        default=None,
        description="The title to show. If not provided, a prettyfied version of the app name will be used.",
    )
    icon: str | None = pydantic.Field(
        default=None,
        description="A font-awesome or google font icon name",
        examples=["fa-brands fa-artstation", "stat_shine"],
    )
    # TODO: find a way to specify color in #FFFFFF so qt app can use it.
    color: str | None = pydantic.Field(
        default=None,
        description="The color to use when showing the app in UIs (see https://quasar.dev/style/color-palette#color-list)",
    )

    # TODO: find out if there's interest in have those in defaults two:
    # needs_dialog: bool = False
    # enabled: bool = True
    # hidden: bool = False

    # installed_versions: set[str] = set()


class ShellAppInfo(pydantic.BaseModel):
    # model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    app: object  # pointer to the app TODO: find a more elegant way to fix the import loop.
    title: str
    icon: str | None = pydantic.Field(
        default=None,
        description="A font-awesome or google font icon name",
        examples=["fa-brands fa-artstation", "stat_shine"],
    )
    color: str | None = None

    needs_dialog: bool = False
    enabled: bool = True
    hidden: bool = False

    installed_versions: set[str] = set()

    @property
    def app_id(self) -> str:
        return self.app.app_id  # type: ignore Trust Me Sis©

    @property
    def groups(self) -> set[str]:
        return self.app.app_groups.copy()  # type: ignore Trust Me Sis©

    def run_app(
        self,
        detach: bool = True,
        notify: Callable[[str], None] | None = None,
        **options: dict[str, Any],
    ):
        run_app_process(
            app=self.app,  # type: ignore Trust Me Sis©
            detach=detach,
            notify=notify,
            **options,
        )
