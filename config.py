"""
Read and parse values from `config.ini` into their appropriate types, 
to be referenced by other modules.
"""
# Non-local imports
import alpaca_trade_api as alpaca_api

# Local imports
import configparser
import sys  # ensure Python > 3.10

# Project modules
import keys


# Ensure Python > 3.10
if sys.version_info < (3, 10):
    raise Exception("You must use Python 3.10 or later.")


# ---- Exceptions ----

class ParameterError(Exception):
    """
    If invalid parameters values are given in config.ini.
    """
    pass

class AccountError(Exception):
    """
    If there's something wrong with the account, ex. margin
    unavailable with a multiplier set.
    """
    pass


# ---- Ensure margin if requested ----

alpaca = alpaca_api.REST(
    key_id = keys.Alpaca.API_KEY,
    secret_key = keys.Alpaca.API_SECRET,
    base_url = keys.Alpaca.BASE_URL
)

def account_margin_status() -> bool:
    """
    Returns True if the account has margin enabled and 
    a positive, tradable margin balance.
    """
    account = alpaca.get_account()
    if float(account.multiplier) > 1:
        return True

    return False
    

class Config:
    """
    Parse parameter values from config.ini in their appropriate types, 
    to be referenced by other modules.
    """
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Portfolio
    portfolio_type = config['Portfolio']['portfolio_type'].title()
    account_multiplier = float(
        config['Portfolio']['account_multiplier'].replace('x', '')  # ex. if '2x' given
    )

    # Ensure account multiplier is reasonable
    if not 0 < account_multiplier <= 2:
        raise ParameterError("Your account multiplier must be between 0 and 2.")

    # Ensure margin is enabled if multiplier > 1
    if account_multiplier > 1 and not account_margin_status():
        raise AccountError("You must have margin enabled to have a multiplier higher than 1.")

    # Rebalancing
    rebalance_threshold = float(config["Rebalancing"]["rebalance_threshold"])

    # Reports
    if config['Reports']['text_reports'].lower() == 'false':
        text_reports = False
    else:
        text_reports = True

    # Email recipients
    _email_recipients = [keys.User.email_address]
    _email_recipients.extend(config['Reports']['additional_recipients'].split(', '))
    email_recipients = [email for email in _email_recipients if email != '']
