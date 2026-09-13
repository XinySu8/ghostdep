from pathlib import Path
from unittest.mock import patch

from ghostdep.checker import PackageResult, Status
from ghostdep.mcp_server import check_manifest, check_packages


@patch("ghostdep.mcp_server.check_package")
def test_check_packages_reports_exists_and_not_found(mock_check):
    mock_check.side_effect = [
        PackageResult("requests", Status.EXISTS),
        PackageResult("fake-lib-xyz-does-not-exist", Status.NOT_FOUND),
    ]
    result = check_packages(["requests", "fake-lib-xyz-does-not-exist"])
    assert result["results"] == [
        {"name": "requests", "status": "exists", "detail": ""},
        {"name": "fake-lib-xyz-does-not-exist", "status": "not_found", "detail": ""},
    ]
    assert result["safe_to_install"] is False
    assert result["blocked"] == ["fake-lib-xyz-does-not-exist"]
    assert result["suggested_command"] == "pip install requests"


@patch("ghostdep.mcp_server.check_package")
def test_check_packages_all_exist_is_safe_to_install(mock_check):
    mock_check.side_effect = [
        PackageResult("requests", Status.EXISTS),
        PackageResult("fastapi", Status.EXISTS),
    ]
    result = check_packages(["requests", "fastapi"])
    assert result["safe_to_install"] is True
    assert result["blocked"] == []
    assert result["suggested_command"] == "pip install requests fastapi"


@patch("ghostdep.mcp_server.check_package")
def test_check_packages_attaches_suggested_replacement_for_a_typo(mock_check):
    mock_check.return_value = PackageResult("reqeusts", Status.NOT_FOUND)
    result = check_packages(["reqeusts"])
    assert result["results"][0]["suggested_replacement"] == "requests"
    # a suggestion is never auto-installed - the blocked name stays blocked,
    # and the real "requests" is not silently substituted into the command
    assert result["safe_to_install"] is False
    assert result["suggested_command"] is None


def test_check_packages_rejects_invalid_name_without_querying_pypi():
    with patch("ghostdep.mcp_server.check_package") as mock_check:
        result = check_packages(["../simple"])
        mock_check.assert_not_called()
    assert result["results"] == [{"name": "../simple", "status": "error", "detail": "invalid package name"}]
    assert result["safe_to_install"] is False


@patch("ghostdep.mcp_server.check_package")
def test_check_manifest_reads_requirements_txt(mock_check, tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("requests==2.31.0\n")
    mock_check.return_value = PackageResult("requests", Status.EXISTS)

    result = check_manifest(str(req))
    assert result["results"] == [{"name": "requests", "status": "exists", "detail": ""}]
    assert result["safe_to_install"] is True


def test_check_manifest_missing_file_returns_error_entry(tmp_path: Path):
    missing = tmp_path / "does-not-exist.txt"
    result = check_manifest(str(missing))
    assert result["results"] == [{"name": str(missing), "status": "error", "detail": "file not found"}]
    assert result["safe_to_install"] is False


def test_check_manifest_poetry_format_returns_error_entry(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[tool.poetry.dependencies]\nrequests = "^2.31"\n')

    result = check_manifest(str(pyproject))
    assert len(result["results"]) == 1
    assert result["results"][0]["status"] == "error"
    assert "Poetry-style" in result["results"][0]["detail"]


def test_check_manifest_malformed_toml_returns_error_entry(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("this is not valid toml [[[")

    result = check_manifest(str(pyproject))
    assert len(result["results"]) == 1
    assert result["results"][0]["status"] == "error"


def test_check_manifest_empty_dependencies_returns_error_entry(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"\ndependencies = []\n')

    result = check_manifest(str(pyproject))
    assert result["results"] == [
        {"name": str(pyproject), "status": "error", "detail": "no dependencies found"}
    ]
