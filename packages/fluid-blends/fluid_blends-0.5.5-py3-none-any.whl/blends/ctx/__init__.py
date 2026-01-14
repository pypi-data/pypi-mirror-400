import os
from collections.abc import Iterator
from pathlib import Path

CPU_CORES = os.cpu_count() or 1
STATE_FOLDER: str = str(Path("~/.blends").expanduser())
STATE_FOLDER_DEBUG = Path(STATE_FOLDER) / "debug"


Path(STATE_FOLDER).mkdir(mode=0o700, exist_ok=True, parents=True)
Path(STATE_FOLDER_DEBUG).mkdir(mode=0o700, exist_ok=True, parents=True)


class _Context:
    def __init__(self) -> None:
        self.feature_flags: set[str] = set[str]()
        self.multi_path: set[Path] = set[Path]()

    def set_feature_flag(self, feature_flag: str) -> None:
        self.feature_flags.add(feature_flag)

    def has_feature_flag(self, feature_flag: str) -> bool:
        return feature_flag in self.feature_flags

    def add_multi_path(self, path: Path) -> None:
        self.multi_path.add(path)

    def iterate_multi_paths(self) -> Iterator[Path]:
        return iter(self.multi_path)


ctx = _Context()
