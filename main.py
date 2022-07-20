# Local imports
import time

# Project modules
import allocation
import rebalancing
import reports
import utils
import errors


def main() -> None:
    """Executes `buy_assets` every day at market open."""
    while True:
        if utils.market_open():
            rebalances = rebalancing.rebalance_portfolio()
            allocations = allocation.allocate_cash()
            reports.deliver_update(allocations, rebalances)
            time.sleep(43_200)  # sleep for half a day
        else:
            time.sleep(60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        errors.report_error(f"Program crashed. Error: {str(e)}.")
