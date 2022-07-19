# Local imports
import time

# Project modules
import allocation
import rebalancing
import texts
import utils
import errors


def deliver_update(rebalances: dict[str, float], allocations: dict[str, float]):
    """Texts an update of all that was done. Eventually, this will use email."""
    texts.text_me(
        f"""
        Rebalances attemped: {rebalances}

        Allocations made: {allocations}
        """
    )


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
