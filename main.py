# Local imports
import time

# Project modules
import allocation
import rebalancing
import utils
import errors


def main() -> None:
    """Executes `buy_assets` every day 10 minutes before market close."""
    while True:
        if utils.market_open():
            rebalancing.rebalance_portfolio()
            allocation.allocate()
            time.sleep(86400)
        else:
            time.sleep(60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        errors.report_error(f"Program crashed. Error: {str(e)}.")
