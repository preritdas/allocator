"""
Read and parse values from `config.ini` into their appropriate types, 
to be referenced by other modules.
"""
import configparser
import keys


class ParameterError(Exception):
    """
    If invalid parameters values are given in config.ini.
    """
    pass
    

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
