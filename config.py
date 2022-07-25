import configparser
import _keys

# Config
class Config:
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Allocation
    portfolio_type = config['Portfolio']['portfolio_type'].title()

    # Rebalancing
    rebalance_threshold: float = float(config["Rebalancing"]["rebalance_threshold"])

    # Reports
    if config['Reports']['text_reports'].lower() == 'false':
        text_reports = False
    else:
        text_reports = True

    # Email recipients
    _email_recipients = [_keys.User.email_address]
    _email_recipients.extend(config['Reports']['additional_recipients'].split(', '))
    email_recipients = [email for email in _email_recipients if email != '']
