# Non-local imports
from alpaca_trade_api.rest import APIError  # handle this error

# Local imports
import threading
import time

# Project modules
from config import Config
import utils
from utils import alpaca
import errors
from allocation import allocation  # the dictionary


# Define an ETFs dictionary with ideal allocations by symbol
etf_allocations = {value[1]: value[0] for value in allocation.values()}


def _fractional_order_errorhandling(side: str, symbol: str, amount: float):
    """Calls `utils.fractional_order` but handles errors if they come up.
    This was designed for use in rebalancing orders, to skip a symbol if 
    there isn't enough buying power due to timing or other reason."""
    try:
        utils.fractional_order(side, symbol, amount)
    except APIError as e:
        if str(e) == 'insufficient buying power':
            errors.report_error(
                f"Error rebalancing {symbol} with {side} order for ${amount}. Skipped."
            )
        else:
            raise APIError(e)


def _current_positions() -> dict[str, float] | str:
    """Returns a dictionary with keys being the symbol name and values
    being a float of the market value of the position in the account.
    Only searches for symbols mentioned in the allocation."""
    etfs: list[str] = [value[1] for value in allocation.values()]
    try:
        return {etf: float(alpaca.get_position(etf).market_value) for etf in etfs}
    except APIError as e:
        if str(e) == "position does not exist":
            return(
                "Positions not found. " 
                "Allow allocation to automatically allocate account cash."
            )

def positional_deltas() -> dict[str, float] | str:
    """Returns a dict of how off each position is in the account based on the
    ideal etf allocations. A negative value means the account is _under_ the
    expectation, so more of it should be bought to compensate."""
    account_total = utils.account_equity()
    positions = _current_positions()

    if isinstance(positions, str):  # if there was an ignorable error
        return positions

    ideal_alloc = {}
    for etf, alloc in etf_allocations.items():
        ideal_alloc[etf] = alloc * account_total

    return_deltas = {}
    for position in positions:
        delta = round((positions[position] - ideal_alloc[position]), 2)
        
        # Only if above threshold and if notional value is more than 2
        if(
            abs(delta) / ideal_alloc[position] > Config.rebalance_threshold
            and abs(delta) > 2
        ):
            return_deltas[position] = delta

    return return_deltas


def rebalance_portfolio() -> dict[str, float] | str:
    """
    Places orders and returns deltas.
    
    `'buy if delta < 0` because if `delta < 0` it means the account is _under_ 
    the ideal allocation. 
    """
    # Ensure no other positions are in the account
    account_positions = [position.symbol for position in alpaca.list_positions()]
    acceptable_etfs = [value[1] for value in allocation.values()]
    if any([True for position in account_positions if position not in acceptable_etfs]):
        return "Cannot rebalance portfolio as untracked positions were detected."

    deltas = positional_deltas()
    if isinstance(deltas, str):  # if there was an ignorable, deliverable error
        return deltas

    # Sell orders first to free up buying power
    for position, delta in deltas.items():
        if delta > 0:
            thread = threading.Thread(
                target = _fractional_order_errorhandling,
                args = ('sell', position, abs(delta))
            )
            thread.start()

    # Sleep to ensure execution
    time.sleep(5)

    # Buy orders next
    for position, delta in deltas.items():
        if delta < 0:
            thread = threading.Thread(
                target = _fractional_order_errorhandling,
                args = ('buy', position, abs(delta))
            )
            thread.start()

    return deltas
