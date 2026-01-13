import pytest
from httpstatusx import HTTP

def test_basic_lookup():
    assert HTTP["ok"] == 200
    assert HTTP["not_found"] == 404

def test_reverse_lookup():
    assert HTTP.name(200) == "ok"
    assert HTTP.name(404) == "not_found"

def test_category():
    assert HTTP.category(200) == "success"
    assert HTTP.category(404) == "client_error"
    assert HTTP.category(503) == "server_error"

def test_is_error():
    assert HTTP.is_error(400) is True
    assert HTTP.is_error(200) is False

def test_invalid_name():
    with pytest.raises(KeyError):
        HTTP["this_does_not_exist"]

def test_invalid_code():
    with pytest.raises(ValueError):
        HTTP.name(999)