import alpaca_trade_api as alpaca_api

import multiprocessing as mp
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

def calculate_quantities(cash_balance: float = cash_balance()):
    """
    Returns a dictionary of the dollar values for each ETF.
    Takes a cash_balance float parameter which defaults to 
    getting the account cash balance using the cash_balance
    method.
    """
    quantities = {}
    for alloc, etf in zip(allocation, etfs):
        amount = cash_balance * allocation[alloc]
        quantities[etfs[alloc]] = round(amount, 3)
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

def buy_assets(quantities: dict = calculate_quantities()):
    """
    Uses multiprocessing to execute the orders. 
    Buys the ETFs in the amounts dictated by the 
    quantities parameter. This is defaulted to the output of
    the calculate_quantities method.
    Returns nothing.
    """
    for symbol, amount in quantities.items():
        process = mp.Process(
            target = fractional_order, 
            args = ('buy', symbol, amount)
        )
        process.start()

if __name__ == "__main__":
    buy_assets()