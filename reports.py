# Non-local imports
import mypytoolkit as kit

# Project modules
import delivery
import allocation
from allocation import alpaca, Config, sector_from_etf
import utils


def _account_summary() -> str:
    """Creates an account summary string for use in `deliver_update`."""
    # Positions
    account_positions = alpaca.list_positions()
    positions: dict[str, dict[str, float]] = {}
    for position in account_positions:
        positions[sector_from_etf[position.symbol]] = {
            "Market Value": round(float(position.market_value), 2),
            "Unrealized Profit": round(float(position.unrealized_pl), 2)
        }

    positions_str = ""
    for sector, attributes in positions.items():
        positions_str += (
            f"{sector} is "
            f"{'up $' if attributes['Unrealized Profit'] > 0 else 'down -$'}"
            f"{abs(attributes['Unrealized Profit']):,} in total, with a market value of "
            f"${attributes['Market Value']:,}.\n"
        )

    summary = (
        f"The account is {Config.portfolio_type.lower()}, with a "
        f"total market value of ${utils.account_equity(rounding=2):,}. "
        "Below are all positions managed in the account.\n\n"
        f"{positions_str}"
    )

    return summary


def deliver_update(
    allocations: dict[str, float], 
    rebalances: dict[str, float] | str
) -> None:
    """Texts an update of all that was done. Eventually, this will use email."""
    # If both dictionaries are empty
    if not allocations and (isinstance(rebalances, dict) and not rebalances):
        update = (
            "No actions were taken today.\n\n----\n\n"
            "Below is a summary of the account as a whole.\n\n"
            f"{_account_summary()}"
        )
        delivery.text_me(update)
        delivery.email_me(update, subject="Allocator Daily Report")
        return

    sector_from_symbol = {val[1]: key for key, val in allocation.allocation.items()}

    allocations_str = "" if allocations else "No allocations were made today."
    for symbol, amount in allocations.items():
        allocations_str += f"Allocated ${amount} of cash to {sector_from_symbol[symbol]}.\n"

    rebalances_str = "" if rebalances else "No positions were rebalanced today."
    if isinstance(rebalances, str):
        rebalances_str = rebalances
    elif isinstance(rebalances, dict):
        for symbol, delta in rebalances.items():
            if delta < 0:
                rebalances_str += f"Added ${abs(delta)} to {sector_from_symbol[symbol]}.\n"
            elif delta > 0:
                rebalances_str += f"Removed ${abs(delta)} from {sector_from_symbol[symbol]}.\n"

    update = (
        f"The following is a summary report of actions taken/attempted by Allocator "
        f"today, {kit.today_date()}.\n\n"
        "Allocations:\n"
        f"{allocations_str}\n\n"
        "Rebalances:\n"
        f"{rebalances_str}"
        "\n\n"
        "Below is a summary of the account as a whole.\n\n----\n\n"
        f"{_account_summary()}"
        ""
    )

    delivery.text_me(update)
    delivery.email_me(update, subject="Allocator Daily Report")
