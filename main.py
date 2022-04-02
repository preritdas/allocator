import alpaca_trade_api as alpaca_api
import mypytoolkit as kit

import time
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
    "Aggregate Bonds": 0.28
}

etfs = {
    "Domestic Large Cap": 'VOO',
    "Domestic Mid Cap": 'IJH',
    "Domestic Small Cap": 'IJR',
    "International": 'IXUS',
    "Short Term Bonds": 'ISTB',
    "Aggregate Bonds": 'AGG'
}

# Check for equality
for alloc, etf in zip(allocation, etfs):
    if alloc != etf:
        raise Exception(
            "Error matching allocation to etfs in global parameters."
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
            "side parameter of fractiona_order was inputted incorrectly."
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
    """Compiles the message for update on execution."""
    # Calculate quantities instead of using default parameter
    quantities = calculate_quantities()

    # If a notional value was < 1
    if not quantities:
        print("New compile message because quantities were too low.")
        message = ("Allocator is skipping today because "\
            "a quantity was less than 1."
        )
        return message

    message = "Bought "
    for symbol, amount in quantities.items():
        message += f"{amount} of {symbol}, "

    # End the message with a period
    return message[0:-2] + "."

def main():
    """Main execution function."""
    print("Allocator is online.")

    while True:
        # if it's market hours and not saturday or sunday
        if 6.6 < kit.time_decimal() < 19 and kit.weekday_int() <= 5:
            buy_assets()

            # Debrief
            if not calculate_quantities(): # if notional value too low
                message = compile_message()
            else:
                message = (
                    "Allocator has executed orders. " +
                    f"{compile_message()}"
                )
            texts.text_me(message)
            time.sleep(36000) # sleep for 10 hours

if __name__ == "__main__":
    main()