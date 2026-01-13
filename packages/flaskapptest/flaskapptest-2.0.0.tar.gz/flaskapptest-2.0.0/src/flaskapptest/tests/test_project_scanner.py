from flaskapptest.core.project_scanner import ProjectScanner
from pathlib import Path


def test_project_scanner_finds_py_files(tmp_path: Path):
    (tmp_path / "app.py").write_text("print('hello')")
    (tmp_path / "utils.py").write_text("x = 1")

    scanner = ProjectScanner(str(tmp_path))
    files = scanner.scan()

    assert len(files) == 2
    assert all(f.suffix == ".py" for f in files)


def test_project_scanner_ignores_venv(tmp_path: Path):
    venv = tmp_path / "venv"
    venv.mkdir()
    (venv / "ignore.py").write_text("x = 1")

    scanner = ProjectScanner(str(tmp_path))
    files = scanner.scan()

    assert len(files) == 0
