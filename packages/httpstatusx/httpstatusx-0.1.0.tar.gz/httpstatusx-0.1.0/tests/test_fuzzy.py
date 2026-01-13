from httpstatusx import HTTP

def test_fuzzy_unauthorized():
    assert HTTP["unauth"] == 401

def test_fuzzy_timeout():
    assert HTTP["timeout"] in (408, 504)

def test_fuzzy_server():
    assert HTTP["server"] == 500
