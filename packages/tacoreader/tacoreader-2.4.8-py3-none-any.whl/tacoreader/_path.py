"""Path resolution for TACO datasets.

Unified handling of local/remote paths with format auto-detection.
"""

from tacoreader._constants import COLLECTION_JSON, TACOZIP_EXTENSIONS
from tacoreader._exceptions import TacoFormatError
from tacoreader._format import _file_exists, is_remote
from tacoreader.dataset import TacoDataset
from tacoreader.storage import create_backend


class TacoPath:
    """Resolve path: location + kind + loading."""

    def __init__(self, path: str):
        self.original = path.rstrip("/")
        self.remote = is_remote(path)
        self.kind, self.resolved = self._detect()

    def _detect(self) -> tuple[str, str]:
        # TacoCat explicit
        if self.original.endswith(".tacocat"):
            return "tacocat", self.original

        # TacoZip explicit
        if self.original.endswith(TACOZIP_EXTENSIONS):
            return "zip", self.original

        # Directory with .tacocat inside
        tacocat_path = f"{self.original}/.tacocat"
        if _file_exists(tacocat_path, COLLECTION_JSON):
            return "tacocat", tacocat_path

        # Folder with COLLECTION.json
        if _file_exists(self.original, COLLECTION_JSON):
            return "folder", self.original

        raise TacoFormatError(
            f"Cannot detect TACO format: {self.original}\n"
            f"Expected: .tacozip file, .tacocat folder, or directory with COLLECTION.json"
        )

    def load(self, **opts) -> TacoDataset:
        backend = create_backend(self.kind)
        return backend.load(self.resolved, **opts)
