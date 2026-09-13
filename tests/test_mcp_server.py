from pathlib import Path
from unittest.mock import Mock, patch

from ghostdep.mcp_server import check_manifest, check_packages


@patch("ghostdep.mcp_server.check_package")
def test_check_packages_reports_exists_and_not_found(mock_check):
    from ghostdep.checker import PackageResult, Status

    mock_check.side_effect = [
        PackageResult("requests", Status.EXISTS),
        PackageResult("fake-lib-xyz", Status.NOT_FOUND),
    ]
    result = check_packages(["requests", "fake-lib-xyz"])
    assert result == [
        {"name": "requests", "status": "exists", "detail": ""},
        {"name": "fake-lib-xyz", "status": "not_found", "detail": ""},
    ]


def test_check_packages_rejects_invalid_name_without_querying_pypi():
    with patch("ghostdep.mcp_server.check_package") as mock_check:
        result = check_packages(["../simple"])
        mock_check.assert_not_called()
    assert result == [{"name": "../simple", "status": "error", "detail": "invalid package name"}]


@patch("ghostdep.mcp_server.check_package")
def test_check_manifest_reads_requirements_txt(mock_check, tmp_path: Path):
    from ghostdep.checker import PackageResult, Status

    req = tmp_path / "requirements.txt"
    req.write_text("requests==2.31.0\n")
    mock_check.return_value = PackageResult("requests", Status.EXISTS)

    result = check_manifest(str(req))
    assert result == [{"name": "requests", "status": "exists", "detail": ""}]


def test_check_manifest_missing_file_returns_error_entry(tmp_path: Path):
    missing = tmp_path / "does-not-exist.txt"
    result = check_manifest(str(missing))
    assert result == [{"name": str(missing), "status": "error", "detail": "file not found"}]


def test_check_manifest_poetry_format_returns_error_entry(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[tool.poetry.dependencies]\nrequests = "^2.31"\n')

    result = check_manifest(str(pyproject))
    assert len(result) == 1
    assert result[0]["status"] == "error"
    assert "Poetry-style" in result[0]["detail"]


def test_check_manifest_malformed_toml_returns_error_entry(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("this is not valid toml [[[")

    result = check_manifest(str(pyproject))
    assert len(result) == 1
    assert result[0]["status"] == "error"


def test_check_manifest_empty_dependencies_returns_error_entry(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"\ndependencies = []\n')

    result = check_manifest(str(pyproject))
    assert result == [
        {"name": str(pyproject), "status": "error", "detail": "no dependencies found"}
    ]
