import reports


def test_account_summary():
    summary = reports._account_summary()
    assert isinstance(summary, str)
    