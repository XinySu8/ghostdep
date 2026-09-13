from pathlib import Path

from slopcheck.parsers import parse_pyproject_toml, parse_requirements_txt


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
