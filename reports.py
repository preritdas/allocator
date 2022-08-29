"""
Create functions to read the Alpaca account and easily deliver daily reports
given the output of the allocation and rebalancing functions.
"""
# Local imports
import datetime

# Project modules
from config import Config
import delivery
import allocation
from allocation import sector_from_etf
import utils
from utils import alpaca


def _account_summary() -> str:
    """Creates an account summary string for use in `deliver_update`."""
    account_equity = utils.account_equity()

    # Positions
    account_positions = alpaca.list_positions()
    positions: dict[str, dict[str, float]] = {}
    for position in account_positions:
        # If the symbol isn't a tracked ETF, show the actual symbol
        symbol = sector_from_etf.get(position.symbol, position.symbol)
        positions[symbol] = {
            "Market Value": round(float(position.market_value), 2),
            "Unrealized Profit": round(float(position.unrealized_pl), 2)
        }

    positions_str = ""
    for sector, attributes in positions.items():
        positions_str += (
            f"- {sector} is "
            f"{'up $' if attributes['Unrealized Profit'] > 0 else 'down -$'}"
            f"{abs(attributes['Unrealized Profit']):,.2f} in total, with a market value of "
            f"${attributes['Market Value']:,.2f}.\n"
        )

    # Account multiplier string depending on margin or under-usage
    if Config.account_multiplier > 1:
        account_multiplier_msg = (
            "Because your multiplier is greater than 1x, your account is "
            "using margin. "
            "You should expect your positions to be totally valued at "
            f"${(account_equity * Config.account_multiplier):,.2f}. "
            "(If you don't have margin enabled in your account, "
            "or you have less than $2,000 equity, please immediately change "
            "your account multiplier to a value less than 1.) "
        )
    elif Config.account_multiplier < 1:
        account_multiplier_msg = (
            "Because your multiplier is less than 1x, your account "
            "intentionally aims to maintain a cash balance of "
            f"${(account_equity * (1 - Config.account_multiplier)):,.2f}. "
            "You should expect your positions to be totally valued at "
            f"${(account_equity * Config.account_multiplier):,.2f}. "
        )
    else:  # if it is equal to 1
        account_multiplier_msg = (
            "Because your multiplier is set to 1x, your account is utilizing its full "
            "cash balance; no more, no less. You should expect your positions "
            f"to be totally valued at ${account_equity:,.2f}, equivalent to your "
            "account equity."
        )

    summary = (
        f"Your account is {Config.portfolio_type.lower()}, with a "
        f"total market value of ${account_equity:,.2f}. "
        f"It's operating at a "
        f"{(1 if Config.account_multiplier == 1 else Config.account_multiplier):.2f}"
        f"x multiplier. {account_multiplier_msg}\n\n"
    )

    # Positions
    if positions:
        summary += (
            "All positions managed in the account are listed below.\n\n"
            f"{positions_str}"
        )
    else:
        summary += (
            "Your account has no positions."
        )

    return summary


def deliver_update(
    allocations: dict[str, float], 
    rebalances: dict[str, float] | str
) -> None:
    """Texts an update of all that was done. Eventually, this will use email."""
    sector_from_symbol = {val[1]: key for key, val in allocation.allocation.items()}

    # Move non-sold rebalances to cash allocation where they belong
    if rebalances and isinstance(rebalances, dict):
        # Check that all rebalances were underneath ideal, thus only cash was allocated
        if not any(amount for amount in rebalances.values() if amount > 0):
            for symbol, amount in rebalances.items(): 
                allocations[symbol] = -amount  # flip sign as rebalances work backwards

            rebalances = {}  # reset as all actions are now handled as allocations

    allocations_str = "" if allocations else "No cash allocations were made today."
    for symbol, amount in allocations.items():
        allocations_str += f"- Allocated ${amount:,.2f} of cash to {sector_from_symbol[symbol]}.\n"

    rebalances_str = "" if rebalances else "No positions were rebalanced today."
    if isinstance(rebalances, str):
        rebalances_str = rebalances
    elif isinstance(rebalances, dict):
        for symbol, delta in rebalances.items():
            if delta < 0:
                rebalances_str += f"- Added ${abs(delta):,.2f} to {sector_from_symbol[symbol]}.\n"
            elif delta > 0:
                rebalances_str += f"- Removed ${abs(delta):,.2f} from {sector_from_symbol[symbol]}.\n"

    # If both dictionaries are empty
    if not allocations and (isinstance(rebalances, dict) and not rebalances):
        update = (
            "No actions were taken today. "
            f"The date is {datetime.date.today().strftime('%A, %B %d, %Y')}.\n\n"
        )
    else:
        update = (
            f"The following is a summary report of actions taken by Allocator today. "
            f"The date is {datetime.date.today().strftime('%A, %B %d, %Y')}.\n\n"
            "Allocations:\n"
            f"{allocations_str}\n\n"
            "Rebalances:\n"
            f"{rebalances_str}"
            "\n\n"
        )
        
    # Append account summary
    update += (
            "----\nThe following is a summary of the account as a whole.\n\n"
            f"{_account_summary()}"
            ""
        )

    if Config.text_reports:
        delivery.text_me(update)
    delivery.email_me(update, subject="Allocator Daily Report")
