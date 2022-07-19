"""Market clock, etc."""

# Non-local imports
import mypytoolkit as kit
import alpaca_trade_api as alpaca_api

# Local imports
import math

# Project modules
import _keys


# Instantiate Alpaca API
alpaca = alpaca_api.REST(
    key_id = _keys.Alpaca.API_KEY,
    secret_key = _keys.Alpaca.API_SECRET,
    base_url = _keys.Alpaca.BASE_URL
)


# Market clock
last_market_open_verification: float = 0.00

def market_open() -> bool:
    global last_market_open_verification

    if 1 <= kit.weekday_int() <= 5 and 9.5 < kit.time_decimal() < 16:
        if(
            math.floor(kit.time_decimal()) == math.floor(last_market_open_verification)
            and math.ceil(round(kit.time_decimal() % 1, 5) * 2) == \
                math.ceil(round(last_market_open_verification % 1, 5)) * 2
        ):
            return True
        elif alpaca.get_clock().is_open:
            last_market_open_verification = kit.time_decimal()
            return True
        else:
            return False
