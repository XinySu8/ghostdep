from unittest.mock import patch

from slopcheck.checker import PackageResult, Status
from slopcheck.cli import main


@patch("slopcheck.cli.check_package")
def test_main_returns_nonzero_when_package_not_found(mock_check):
    mock_check.return_value = PackageResult("fake-pkg", Status.NOT_FOUND)
    assert main(["fake-pkg"]) == 1


@patch("slopcheck.cli.check_package")
def test_main_returns_zero_when_all_exist(mock_check):
    mock_check.return_value = PackageResult("requests", Status.EXISTS)
    assert main(["requests"]) == 0
