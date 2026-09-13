from ghostdep.suggest import suggest_replacement


def test_suggests_replacement_for_a_close_typo():
    assert suggest_replacement("reqeusts") == "requests"


def test_no_suggestion_for_an_unrelated_name():
    assert suggest_replacement("fast-super-secure-lib-that-does-not-exist") is None
