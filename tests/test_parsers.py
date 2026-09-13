from pathlib import Path

from ghostdep.parsers import (
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


def test_poetry_style_pyproject_yields_no_names(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.poetry.dependencies]\n'
        'requests = "^2.31"\n'
    )
    assert parse_pyproject_toml(pyproject) == []


def test_is_valid_package_name():
    assert is_valid_package_name("requests")
    assert is_valid_package_name("some-pkg_2.0")
    assert not is_valid_package_name("../simple")
    assert not is_valid_package_name("pkg name")
    assert not is_valid_package_name("")
