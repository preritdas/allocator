"""Account, orders, market clock, etc."""
# Non-local imports
import mypytoolkit as kit
import alpaca_trade_api as alpaca_api
from rich.console import Console; console = Console()

# Local imports
import math

# Project modules
import keys
from config import Config


# Instantiate Alpaca API
alpaca = alpaca_api.REST(
    key_id = keys.Alpaca.API_KEY,
    secret_key = keys.Alpaca.API_SECRET,
    base_url = keys.Alpaca.BASE_URL
)


# ---- Account and orders ----

def account_margin_status() -> bool:
    """
    Returns True if the account has margin enabled and 
    a positive, tradable margin balance.
    """
    account = alpaca.get_account()
    if float(account.multiplier) > 1:
        return True

    return False


def account_equity(rounding: int = None) -> float:
    equity = float(alpaca.get_account().equity)
    if not rounding:
        return equity

    return round(equity, rounding)


def tradable_balance() -> float:
    """
    Reads available cash to trade and returns a float.
    Accounts for account multiplier.
    """
    account = alpaca.get_account()
    return float(account.cash) * Config.account_multiplier


def fractional_order(side: str, symbol: str, amount: float) -> None:
    """Give `side` as 'buy' or 'sell'."""
    side = side.lower()
    if side not in ('buy', 'sell'):
        raise Exception("Side parameter was inputted incorrectly.")

    # Submit the order
    alpaca.submit_order(
        symbol = symbol,
        side = side,
        notional = amount,
    )


# --- Market clock ---- 

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

    return False
