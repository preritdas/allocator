import utils


def test_market_open():
    """
    Test it twice to use the local cached if the market is open.
    """
    market_open = utils.market_open()
    if market_open:
        assert utils.market_open()  # run again using cached


def test_tradable_balance():
    assert utils.tradable_balance()


def test_margin_status():
    res = utils.account_margin_status()
    assert isinstance(res, bool)
