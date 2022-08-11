"""
Defines the `allocation` dict with sectors, proportional allocation,
and the associate ETF to be executed. 

Raises an exception if the giver proportions sum to more than 1; i.e., if 
more than the total account value is to be allocated to various sectors.
"""
# Local imports
import threading
import json  # parse portfolios database
import os  # ensure portfolios database exists

# Project modules
from config import Config
import utils


class PortfolioNotFoundError(Exception):
    pass

# Ensure portfolios.json file has been created
if not os.path.exists(
    (
        portfolio_db_path := os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'portfolios.json')
    )
):
    raise Exception(
        "You must have a portfolios.json database, it comes with the repository."
    )

with open(portfolio_db_path, 'r') as portfolios_file:
    _all_portfolios: dict[str, dict[str, list[float, str]]] = json.load(portfolios_file)
    if not Config.portfolio_type in _all_portfolios.keys():
        raise PortfolioNotFoundError(f"{Config.portfolio_type} not found in portfolios database.")

    allocation: dict[str, list[float, str]] = _all_portfolios[Config.portfolio_type]
    
    # Preserve tuple immutability for values: convert list values to tuple
    allocation: dict[str, tuple[float, str]] = {
        key: tuple(val) for key, val in allocation.items()
    }

# Enable reverse lookup, relied on by reports module
sector_from_etf = {val[1]: key for key, val in allocation.items()}


# Checking for total account allocation size
if sum(val[0] for val in allocation.values()) > 1:
    raise Exception(
        "Allocations in parameters must be less than or equal to 1 full account size."
    )


def calculate_quantities() -> dict[str, float]:
    # Only allow cash allocations if multiplier results in zero/sub-zero cash reserve
    if (reserved_cash := (1 - Config.account_multiplier) * utils.account_equity()) < 0:
        if not Config.account_multiplier > 1: return {}  # pure cash based allocation

    # Ensure there's enough surplus cash to allocate (i.e. all available not reserved)
    if (cash_balance := float(utils.alpaca.get_account().cash)) - reserved_cash < 0:
        return {}

    # Subtract reserved cash if multiplier is under 1, otherwise naked cash allocation
    if Config.account_multiplier > 1: tradable_cash = cash_balance
    elif Config.account_multiplier <= 1: tradable_cash = cash_balance - reserved_cash

    quantities = {}
    for alloc in allocation.values():
        amount = alloc[0] * tradable_cash
        if amount < 2: return {}
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
