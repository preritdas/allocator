# Local imports
import time

# Project modules
import allocation
import rebalancing
import delivery
import utils
import errors


def deliver_update(rebalances: dict[str, float], allocations: dict[str, float]):
    """Texts an update of all that was done. Eventually, this will use email."""
    update = (
        f"""
        Rebalances attemped: {rebalances}

        Allocations made: {allocations}
        """
    )

    delivery.text_me(update)
    delivery.email_me(update, subject="Allocator Daily Report")


def main() -> None:
    """Executes `buy_assets` every day 10 minutes before market close."""
    while True:
        if utils.market_open():
            attempted_rebalances = rebalancing.rebalance_portfolio()
            allocations = allocation.allocate()
            deliver_update(attempted_rebalances, allocations)
            time.sleep(86400)
        else:
            time.sleep(60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        errors.report_error(f"Program crashed. Error: {str(e)}.")
