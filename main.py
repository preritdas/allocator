# External imports
import mypytoolkit as kit  # date string

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
            with utils.console.status("Delaying deployment until the next market day."):
                time.sleep(7 * 60)  # sleep for seven hours, market day + 0.5 hours
        elif deploy_option != 'delay':  # if unrecognized option is given
            utils.console.log(
                f"Unrecognized option, {deploy_option}. "
                "Did you mean 'delay'?"
            )
            return

    while True:
        with utils.console.status("Waiting until the market opens."):
            while not utils.market_open(): time.sleep(60)

        with utils.console.status("Rebalancing the portfolio."):
            rebalances = rebalancing.positional_deltas()
            # rebalances = rebalancing.rebalance_portfolio()
            time.sleep(5)  # ensure positions can be recognized by subsequent calls

        with utils.console.status("Allocating free cash."):
            allocations = allocation.calculate_quantities()
            # allocations = allocation.allocate_cash()
            time.sleep(5)  

        with utils.console.status("Delivering a report by email."):
            reports.deliver_update(allocations, rebalances)
        
        utils.console.log(f"Completed account revision on {kit.full_date_string()}.")

        with utils.console.status("Sleeping until the market closes."):
            while utils.market_open(): time.sleep(60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        errors.report_error(f"Program crashed. Error: {str(e)}.")
