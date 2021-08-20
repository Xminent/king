from pathlib import Path
from .base import Manager


class PrefixManager(Manager):
    path_ = Path("core/data/prefixes.yaml")

    def __init__(self, config: dict) -> None:
        super().__init__(PrefixManager.path_)
        self._config: dict = config


class BlacklistManager(Manager):
    path_ = Path("core/data/blacklist.yaml")

    def __init__(self, config: dict) -> None:
        super().__init__(BlacklistManager.path_)
        self._config: dict = config
