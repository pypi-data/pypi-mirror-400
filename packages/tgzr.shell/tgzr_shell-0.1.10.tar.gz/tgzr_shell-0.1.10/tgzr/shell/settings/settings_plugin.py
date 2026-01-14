from __future__ import annotations
from typing import TYPE_CHECKING

from .settings_provider import BaseSettingsProvider
from .settings_provider import (
    SettingsModelType,
)  # for transitiv imports

if TYPE_CHECKING:
    from ..session import Session


class SettingsProviderPlugin:

    def __init__(self, session: Session) -> None:
        pass

    def handles(self, url: str) -> bool:
        return True

    def create_provider(self, url: str) -> BaseSettingsProvider:
        raise NotImplementedError()
