"""Defines the `allocation` dict with sectors, proportional allocation,
and the associate ETF to be executed. 

Raises an exception if the giver proportions sum to more than 1; i.e., if 
more than the total account value is to be allocated to various sectors."""


# Non-local imports
import alpaca_trade_api as alpaca_api

# Local imports
import multiprocessing as mp

# Project modules
import allocation
import _keys


allocation = {
    "Domestic Large Cap": (0.35, "VOO"),
    "Domestic Mid Cap": (0.05, "IJH"),
    "Domestic Small Cap": (0.02, "IJR"),
    "International": (0.18, "IXUS"),
    "Short Term Bonds": (0.12, "ISTB"),
    "Aggregate Bonds": (0.28, "AGG")
}


# Checking for total account allocation size
total_account = 0
for val in allocation.values():
    total_account += val[0]

if total_account > 1:
    raise Exception("Allocations in parameters must be less than or equal to 1 full account size.")


# Instantiate Alpaca API
alpaca = alpaca_api.REST(
    key_id = _keys.Alpaca.API_KEY,
    secret_key = _keys.Alpaca.API_SECRET,
    base_url = _keys.Alpaca.BASE_URL
)


def _cash_balance() -> float:
    """Reads available cash to trade and returns a float."""
    account = alpaca.get_account()
    return float(account.cash)


def calculate_quantities() -> dict[str, float]:
    quantities = {}
    cash = _cash_balance()

    for alloc in allocation.allocation.values():
        amount = alloc[0] * cash
        if amount < 2:
            return {}
        quantities[alloc[1]] = round(amount, 2)

    return quantities


def _fractional_order(side: str, symbol: str, amount: float) -> None:
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


def allocate() -> dict:
    """Submits orders based on `calculate_quantities`."""
    quantities = calculate_quantities()

    for symbol, amount in quantities.items():
        process = mp.Process(
            target = _fractional_order,
            args = ('buy', symbol, amount)
        )
        process.start()

    return quantities
