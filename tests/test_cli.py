from pathlib import Path
from unittest.mock import patch

import pytest

from ghostdep.checker import PackageResult, Status
from ghostdep.cli import main


@patch("ghostdep.cli.check_package")
def test_main_returns_nonzero_when_package_not_found(mock_check):
    mock_check.return_value = PackageResult("fake-pkg", Status.NOT_FOUND)
    assert main(["fake-pkg"]) == 1


@patch("ghostdep.cli.check_package")
def test_main_returns_zero_when_all_exist(mock_check):
    mock_check.return_value = PackageResult("requests", Status.EXISTS)
    assert main(["requests"]) == 0


def test_main_exits_cleanly_on_missing_file(tmp_path: Path, capsys):
    missing = tmp_path / "does-not-exist.txt"
    with pytest.raises(SystemExit):
        main(["--file", str(missing)])
    assert "file not found" in capsys.readouterr().err


def test_main_rejects_invalid_package_name(capsys):
    with pytest.raises(SystemExit):
        main(["../simple"])
    assert "invalid package name" in capsys.readouterr().err


def test_main_reports_unsupported_pyproject_format(tmp_path: Path, capsys):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.poetry.dependencies]\n'
        'requests = "^2.31"\n'
    )
    with pytest.raises(SystemExit):
        main(["--file", str(pyproject)])
    assert "Poetry-style" in capsys.readouterr().err
