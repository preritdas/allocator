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
            with utils.console.status(
                "Market is still open. Delaying deployment until the next market day."
            ):
                while utils.market_open(): time.sleep(1)  
        elif deploy_option != 'delay':  # if unrecognized option is given
            utils.console.log(
                f"Unrecognized option, {deploy_option}. "
                "Did you mean 'delay'?"
            )
            return

    status = utils.console.status("")
    while True: 
        with status:
            status.update("Waiting for the market to open.")
            while not utils.market_open(): time.sleep(3)

            # Market is open. Log new lines to console.
            utils.console.line()
            utils.console.rule(kit.full_date_string())
            utils.console.log("Market is open. Beginning account revision.")

            status.update("Rebalancing the portfolio.")
            rebalances = rebalancing.rebalance_portfolio()
            time.sleep(5)  # ensure positions can be recognized by subsequent calls

            status.update("Allocating free cash.")
            allocations = allocation.allocate_cash()
            time.sleep(5)  

            status.update("Compiling and delivering a report by email.")
            reports.deliver_update(allocations, rebalances)
        
            utils.console.log(f"Completed account revision on {kit.full_date_string()}.")

            status.update("Sleeping until the market closes.")
            while utils.market_open(): time.sleep(60)

            # New line for new day
            utils.console.line()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        errors.report_error(f"Program crashed. Error: {str(e)}.")
