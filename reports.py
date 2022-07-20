# Non-local imports
import mypytoolkit as kit

# Project modules
import delivery
import allocation


def deliver_update(allocations: dict[str, float], rebalances: dict[str, float]) -> None:
    """Texts an update of all that was done. Eventually, this will use email."""
    # If both dictionaries are empty
    if not allocations and not rebalances:
        update = "No actions were taken today."
        delivery.text_me(update)
        delivery.email_me(update, subject="Allocator Daily Report")
        return

    sector_from_symbol = {val[1]: key for key, val in allocation.allocation.items()}

    allocations_str = "" if allocations else "No allocations were made today."
    for symbol, amount in allocations.items():
        allocations_str += f"Allocated ${amount} of cash to {sector_from_symbol[symbol]}.\n"

    rebalances_str = "" if rebalances else "No positions were rebalanced today."
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
        ""
    )

    delivery.text_me(update)
    delivery.email_me(update, subject="Allocator Daily Report")
