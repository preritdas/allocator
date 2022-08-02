# Local imports
import time
import sys  # argv for deployment delay

# Project modules
import allocation
import rebalancing
import reports
import utils
import errors


def main() -> None:
    """Rebalances and allocates portfolio cash every market day at the open."""
    # Deploy option: delay until next market day
    if len(sys.argv) > 1:  # if an option is provided
        if (deploy_option := sys.argv[1].lower()) == 'delay' and utils.market_open():
            utils.console.log("Delaying deployment until the next market day.")
            time.sleep(7 * 60)  # sleep for seven hours, market day + 0.5 hours
        elif deploy_option != 'delay':  # if unrecognized option is given
            utils.console.log(
                f"Unrecognized option, {deploy_option}. "
                "Did you mean 'delay'?"
            )
            quit()

    # Main logic
    while True:
        if utils.market_open():
            rebalances = rebalancing.rebalance_portfolio()
            time.sleep(5)  # ensure positions can be recognized by subsequent calls

            allocations = allocation.allocate_cash()
            time.sleep(5)  

            reports.deliver_update(allocations, rebalances)
            time.sleep(43_200)  # sleep for half a day
        else:
            time.sleep(60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        errors.report_error(f"Program crashed. Error: {str(e)}.")
