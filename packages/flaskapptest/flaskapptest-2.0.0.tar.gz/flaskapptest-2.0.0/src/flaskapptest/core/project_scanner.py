# flaskapptest/core/project_scanner.py

from pathlib import Path
from typing import List, Set


DEFAULT_EXCLUDED_DIRS: Set[str] = {
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".env",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
}


class ProjectScanner:
    """
    Scans a project directory and returns Python source files.
    """

    def __init__(
        self,
        root_path: str,
        excluded_dirs: Set[str] | None = None,
    ) -> None:
        self.root_path = Path(root_path).resolve()
        self.excluded_dirs = excluded_dirs or DEFAULT_EXCLUDED_DIRS

        if not self.root_path.exists():
            raise FileNotFoundError(f"Path does not exist: {self.root_path}")

        if not self.root_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.root_path}")

    def scan(self) -> List[Path]:
        """
        Recursively scans the project and returns all .py files.
        """
        python_files: List[Path] = []

        for path in self.root_path.rglob("*.py"):
            if self._is_excluded(path):
                continue
            python_files.append(path)

        return python_files

    def _is_excluded(self, path: Path) -> bool:
        """
        Checks whether the file is inside an excluded directory.
        """
        for parent in path.parents:
            if parent.name in self.excluded_dirs:
                return True
        return False
