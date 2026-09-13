from unittest.mock import Mock, patch

import requests

from slopcheck.checker import Status, check_package


@patch("slopcheck.checker.requests.get")
def test_existing_package_returns_exists(mock_get):
    mock_get.return_value = Mock(status_code=200)
    result = check_package("requests")
    assert result.status is Status.EXISTS


@patch("slopcheck.checker.requests.get")
def test_missing_package_returns_not_found(mock_get):
    mock_get.return_value = Mock(status_code=404)
    result = check_package("this-does-not-exist-xyz")
    assert result.status is Status.NOT_FOUND


@patch("slopcheck.checker.requests.get")
def test_network_failure_returns_error_not_exists(mock_get):
    mock_get.side_effect = requests.ConnectionError("boom")
    result = check_package("whatever")
    assert result.status is Status.ERROR


@patch("slopcheck.checker.requests.get")
def test_unexpected_status_returns_error(mock_get):
    mock_get.return_value = Mock(status_code=500)
    result = check_package("whatever")
    assert result.status is Status.ERROR
