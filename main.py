# Non-local imports
import alpaca_trade_api as alpaca_api
import mypytoolkit as kit

# Local imports
import time

# Project modules
import multiprocessing as mp
import texts
import _keys


# Instantiate Alpaca API
alpaca = alpaca_api.REST(
    key_id = _keys.alpaca_API_Key,
    secret_key = _keys.alpaca_API_Secret,
    base_url = _keys.alpaca_base_url
)

# ---- GLOBAL PARAMETERS ----
allocation = {
    "Domestic Large Cap": 0.35,
    "Domestic Mid Cap": 0.05,
    "Domestic Small Cap": 0.02,
    "International": 0.18,
    "Short Term Bonds": 0.12,
    "Aggregate Bonds": 0.23,
    "Crypto": 0.05
}

etfs = {
    "Domestic Large Cap": 'VOO',
    "Domestic Mid Cap": 'IJH',
    "Domestic Small Cap": 'IJR',
    "International": 'IXUS',
    "Short Term Bonds": 'ISTB',
    "Aggregate Bonds": 'AGG',
    "Crypto": 'BTCUSD'
}

# Check for equality
for alloc, etf in zip(allocation, etfs):
    if alloc != etf:
        raise Exception(
            "Error matching allocation to etfs in global parameters."
        )
# Check for total allocation <= 1
allocation_sum = 0
for sector, amount in allocation.items():
    allocation_sum += amount
if allocation_sum > 1:
    raise Exception(
        "The global parameter allocation sums to more than one full account."
    )


def cash_balance():
    """Returns a float of the account cash balance."""
    account = alpaca.get_account()
    cash_balance = float(account.cash)
    return cash_balance

def calculate_quantities():
    """
    Returns a dictionary of the dollar values for each ETF.
    """
    quantities = {}
    cash = cash_balance()
    for alloc, etf in zip(allocation, etfs):
        amount = cash * allocation[alloc]
        quantities[etfs[alloc]] = round(amount, 3)

    # Check for notional value > 1
    for symbol, amount in quantities.items():
        if amount < 1:
            return False
    
    # if all notional values are above 1
    return quantities

def fractional_order(side: str, symbol: str, amount: float):
    """
    Submits a fractional order. Requires parameters for side, 
    symbol, and amount.
    Side is 'buy' or 'sell'. 
    """
    # Check if side is inputted validly
    side = side.lower()
    if side != 'buy' and side != 'sell':
        raise Exception(
            "side parameter of fractional_order was inputted incorrectly."
        )
    
    # Submit the order
    alpaca.submit_order(
        side = side,
        symbol = symbol,
        notional = amount
    )

def buy_assets():
    """
    Uses multiprocessing to execute the orders. 
    Buys the ETFs in the amounts dictated by the 
    quantities parameter.
    Returns True if notional values were high enough for the
    program to make purchases. Returns False if they're not.
    """
    # Compute quantities instead of using default parameter
    quantities = calculate_quantities()

    # if get_quantities returned false due to notional value < 1
    if not quantities:
        print(
            'Buy assets function not running because calculate_quantities',
            'function deemed notional values to be too low.'
        )
        return False

    for symbol, amount in quantities.items():
        process = mp.Process(
            target = fractional_order, 
            args = ('buy', symbol, amount)
        )
        process.start()
    return True

def compile_message():
    """
    Compiles a tuple of the message for update on execution.
    If calculate_quantities returns a False due to 
    notional value being under 1, compile_message 
    will return a message saying Allocator is skipping
    the day.
    """
    # Calculate quantities instead of using default parameter
    quantities = calculate_quantities()

    # If a notional value was < 1
    if not quantities:
        message = ("Allocator is not executing orders today because "\
            "a quantity was less than 1."
        )
        return (message, sector_update())

    message = "Orders have been executed. Bought "
    for symbol, amount in quantities.items():
        message += f"{amount} of {symbol}, "

    # End the message with a period
    return (message[0:-2] + ".", sector_update())

# --- Account Reading ----
def account_equity():
    """Returns a float of the account's current equity value."""
    return float(alpaca.get_account().equity)

def relevant_positions():
    """
    Returns a list of Alpaca positions objects that are covered by the `etfs`.
    """
    alpaca_positions = alpaca.list_positions()
    
    response = []
    for position in alpaca_positions:
        if position.symbol in etfs.values():
            response.append(position)
    
    return response

def true_live_allocation():
    """
    Returns a dictionary, formatted like `allocation`, with
    the true live account allocation by sector.
    """
    true_allocation = {}

    account_positions = alpaca.list_positions()
    for position in account_positions:
        if position.symbol in etfs.values():
            # Get the sector of the symbol with reversed dictionary
            position_sector = kit.reverse_dict(etfs)[position.symbol]
            # Get the proportion of account balance
            proportion = float(position.market_value) / account_equity()
            # Assign results to true_allocation
            true_allocation[position_sector] = proportion

    return true_allocation

def allocation_variance(message: bool = False, allocation_input: dict = None):
    """Returns a dictionary of the difference between true and expected allocation."""
    if allocation_input is None:
        allocation_input = true_live_allocation()
    
    response = {}
    for sector, alloc in allocation_input.items():
        variance = alloc - allocation[sector]
        response[sector] = round(variance * 100, 3)

    if message:
        message_response = ""
        for sector, variance in response.items():
            message_response += f"In our account, {sector} is off by {variance}%. "
        return message_response
    else:
        return response

def sector_update():
    """Returns an update message of daily and lifetime performance per sector."""
    account_positions = relevant_positions()
    
    response = ""
    for position in account_positions:
        position_sector = kit.reverse_dict(etfs)[position.symbol]
        sector_change = round(float(position.change_today), 3)
        sector_direction = "up" if sector_change > 0 else "down"
        lifetime_performance = round(float(position.unrealized_intraday_plpc), 3)
        lifetime_performance_direction = "up" if lifetime_performance > 0 else "down"
        # Sector update
        response += f"{position_sector} is {sector_direction} {sector_change}% today. "
        # Position update
        response += f"Our position is {lifetime_performance_direction} "
        response += f"{lifetime_performance}% cumulatively."

    return response

def main():
    """Main execution function."""
    print("Allocator is online.")

    while True:
        # if it's market hours and not saturday or sunday
        if 6.6 < kit.time_decimal() < 13 and kit.weekday_int() <= 5:
            buy_assets()

            # Debrief
            for message in compile_message():
                texts.text_me(message)

            # Allocation variance (usually Fridays but every day for testing/debugging)
            texts.text_me(allocation_variance(message = True))

            time.sleep(36000) # sleep for 10 hours


if __name__ == "__main__":
    main()