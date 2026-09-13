from pathlib import Path

import pytest

from ghostdep.parsers import (
    UnsupportedManifestFormat,
    is_valid_package_name,
    parse_pyproject_toml,
    parse_requirements_txt,
)


def test_parse_requirements_txt(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text(
        "requests==2.31.0\n"
        "flask>=2.0\n"
        "# a comment\n"
        "\n"
        "-e git+https://example.com/repo.git\n"
        "some-pkg[extra]>=1.0\n"
    )
    assert parse_requirements_txt(req) == ["requests", "flask", "some-pkg"]


def test_parse_pyproject_toml(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\n'
        'name = "demo"\n'
        'dependencies = ["requests>=2.31", "flask"]\n'
    )
    assert parse_pyproject_toml(pyproject) == ["requests", "flask"]


def test_poetry_style_pyproject_raises_unsupported_format(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.poetry.dependencies]\n'
        'requests = "^2.31"\n'
    )
    with pytest.raises(UnsupportedManifestFormat):
        parse_pyproject_toml(pyproject)


def test_hybrid_pyproject_raises_instead_of_silently_dropping_poetry_deps(tmp_path: Path):
    # A file with deps under both [project] and [tool.poetry] must not
    # silently report only the [project] subset as a clean, complete scan.
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\n'
        'dependencies = ["requests"]\n'
        '[tool.poetry.dependencies]\n'
        'flask = "^2.0"\n'
    )
    with pytest.raises(UnsupportedManifestFormat):
        parse_pyproject_toml(pyproject)


def test_genuinely_empty_pep621_project_returns_empty_list(tmp_path: Path):
    # No poetry table at all: an empty dependency list is not mistaken for
    # an unsupported format.
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\n'
        'name = "demo"\n'
        'dependencies = []\n'
    )
    assert parse_pyproject_toml(pyproject) == []


def test_is_valid_package_name():
    assert is_valid_package_name("requests")
    assert is_valid_package_name("some-pkg_2.0")
    assert not is_valid_package_name("../simple")
    assert not is_valid_package_name("pkg name")
    assert not is_valid_package_name("")
