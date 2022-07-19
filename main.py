# Local imports
import time

# Project modules
import allocation
import utils


def main() -> None:
    """Executes `buy_assets` every day 10 minutes before market close."""
    while True:
        if utils.market_open():
            allocation.allocate()
            time.sleep(86400)
        else:
            time.sleep(60)


if __name__ == '__main__':
    main()
