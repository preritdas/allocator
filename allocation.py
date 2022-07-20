"""Defines the `allocation` dict with sectors, proportional allocation,
and the associate ETF to be executed. 

Raises an exception if the giver proportions sum to more than 1; i.e., if 
more than the total account value is to be allocated to various sectors."""


# Non-local imports
import alpaca_trade_api as alpaca_api

# Local imports
import threading
import configparser
import json  # parse portfolios database

# Project modules
import utils
import _keys


# Read user's allocation choice
class Config:
    config = configparser.ConfigParser()
    config.read('config.ini')
    portfolio_type = config['Portfolio']['portfolio_type'].title()

class PortfolioNotFoundError(Exception):
    pass

with open('portfolios.json', 'r') as portfolios_file:
    _all_portfolios: dict[str, dict[str, list[float, str]]] = json.load(portfolios_file)
    if not Config.portfolio_type in _all_portfolios.keys():
        raise PortfolioNotFoundError(f"{Config.portfolio_type} not found in portfolios database.")

    allocation: dict[str, list[float, str]] = _all_portfolios[Config.portfolio_type]
    
    # Preserve tuple immutability for values: convert list values to tuple
    allocation: dict[str, tuple[float, str]] = {
        key: tuple(val) for key, val in allocation.items()
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


def calculate_quantities() -> dict[str, float]:
    quantities = {}
    cash = utils.cash_balance()

    for alloc in allocation.values():
        amount = alloc[0] * cash
        if amount < 2:
            return {}
        quantities[alloc[1]] = round(amount, 2)

    return quantities


def allocate_cash() -> dict:
    """Submits orders based on `calculate_quantities`."""
    quantities = calculate_quantities()

    for symbol, amount in quantities.items():
        process = threading.Thread(
            target = utils.fractional_order,
            args = ('buy', symbol, amount)
        )
        process.start()

    return quantities
