from __future__ import annotations
from typing import TYPE_CHECKING

from pathlib import Path

if TYPE_CHECKING:
    from .session import Session


class System:
    """
    Utility class to manage the "System" folder in a tgzr session home.
    """

    def __init__(self, session: Session):
        self._session = session
        self._path = self._session.home / "System"
        if not self._path.exists():
            self._path.mkdir()

    @property
    def path(self) -> Path:
        return self._path
