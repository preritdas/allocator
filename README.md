![pytest](https://github.com/preritdas/allocator/actions/workflows/pytest.yml/badge.svg)
![coverage](tests/badge.svg)
![versions](https://img.shields.io/badge/python-3.10-blue)
![deployment](https://img.shields.io/badge/deployment-active--deployment-brightgreen)
![maintenance](https://img.shields.io/badge/maintenance-passively--monitored-green)
![Documentation Status](https://readthedocs.org/projects/portfolio-allocator/badge/?version=latest)


# Allocator

Allocator is a fully autonomous, dynamic portfolio manager. It both allocates free cash to predetermined sectors _and_ reads account positions to determine if it should relatively re-balance any positions. (This becomes necessary if certain sectors outperform others, resulting in them occupying a larger than defined portion of the account.)

Watch a one minute recording of Allocator in action!

[![video](readme-content/terminal_video_snapshot.PNG)](https://user-images.githubusercontent.com/96673937/183304943-a0c990ec-5839-4e50-a724-6957c7469231.mp4)

(You can watch the raw shell asciicast [here](https://asciinema.org/a/bMnBp1SnOiryIcjwApuKLHTnE).)

## Portfolios

Allocator's predefined portfolios are adapted from [Acorns](https://acorns.com) Invest's risk profiles. Those are true and tested portfolios, packaged into the local database [portfolios.json](portfolios.json). To select a portfolio, simply update the `portfolio_type` configuration element in [config.ini](config%20(sample).ini). See steps to deployment in the [deployment](#deployment) section. The five currently supported portfolio types are below.

| Portfolio Type | Investment Composition |
| --- | --- |
| Conservative | Ultra short-term corporate and government bonds. |
| Moderately Conservative | Mostly short-term USD/aggregate bonds, with a small exposure in mid-cap and international stocks. |
| Moderate | Primarily domestic/international stocks, with a sizeable exposure to aggregate bonds. |
| Moderately Aggressive | Primarily large domestic stocks, with a sizeable exposure in internationals and domestic bonds. |
| Aggressive | Entirely domestic and international stocks. |

### Account Multiplier

If you want Allocator to make use of available margin in your account, increase the `portfolio_multiplier` in your [config.ini](config%20(sample).ini). The maximum multiplier is 2. You _must_ have margin enabled (with a positive margin buying power) to use this feature; Allocator will warn you at deployment if you don't.

By setting your account multiplier to a value less than 1, you can choose to manage only a fraction of your account, leaving the remaining balance as free cash. When you transfer funds to your account, Allocator will only invest what it can while leaving enough free cash in accordance with your multiplier. 


## Reports

Every day, after Allocator attempts to re-balance the portfolio and allocate free cash, it sends a report of all operations by email and text. A sample daily email report is below. It contains the following information.

(You can choose to not receive daily reports by text by setting `text_reports = false` in your configuration file. You will always receive reports by email, however.)

- Cash allocations
- Rebalanced positions
  - Positions shaved
  - Positions bulked
  - Notice of unrecognized positions (more info below)
  - Notice of positions unallocated
- Account summary
  - Portfolio type (moderate, etc.)
  - Account multiplier, and information on how it's impacting your account
  - Account market value (equity)
  - Each position (including untracked positions) with lifetime unrealized gains and total market value

A screenshot of a sample email report is below.

![Sample Email Report](readme-content/sample_email.PNG)


## Deployment

Only two files need to be modified for deployment: [keys.ini](keys%20(sample).ini) and [config.ini](config%20(sample).ini). See their associated [sections](#keysini) to understand what values are necessary in each file, and how to format them. 

### Deploy delay

If the market is open but you'd like to deploy Allocator to only start operating the following market day, run `python main.py delay` instead of `python main.py`. This is useful, for example, if Allocator already executed orders for the day, but you stopped the program manually to update/redeploy it.

### Deployment steps

1. (Optional but recommended) Use a hosted Linux server (Ubuntu, BASH) for guaranteed uptime, a strong internet connection, and fast data processing.
2. Clone this repository with the command `git clone https://github.com/preritdas/allocator.git`. 
3. Navigate into the repository folder with `cd allocator`. 
4. Create a template keys.ini file using the provided script: `bash scripts/configurate.sh`. 
5. Use an editor to fill out all the fields in `keys.ini`. Either Vim, Nano, or a desktop editor if available.
6. Use an editor to modify any values in `config.ini`, including your portfolio style.
7. Set up dependencies.
   1. Ensure you have Python 3.10.5 (Any version of Python 3.10 should work).
   2. Ensure you have pip and venv. If you don't, install pip by executing [get-pip.py](https://bootstrap.pypa.io/get-pip.py). Install venv by running `sudo apt-get install python3.10-venv -y` on Debian/Ubuntu machines.
   3. Create a virtual environment for Allocator with `python3.10 -m venv venv`, replacing "python3.10" with the correct alias for your Python 3.10 installation.
   4. Activate the environment with `venv/bin/activate` (on Linux/Mac), or with `venv/Scripts/activate` if using Windows.
   5. Install all dependencies with `pip install -r requirements.txt` (in the environment, the `python` and `pip` aliases are correctly linked).
   6. Clear the screen with `clear`, then run Allocator with `python main.py`. 

If you want your script to run forever in the background, as is Allocator's design, use `tmux`. 

1. Create a new tmux session with `tmux new -s allocator`. 
2. Follow the deployment steps above.
3. Exit the session with `:detach`. 

### Shell-based demonstration

The following recording is an example of an entirely shell-based deployment _and_ redeployment (re-cloning to update the source code while maintaining key and config files). 

[![asciicast](https://asciinema.org/a/d0ZMZf1Pqw41NodYv6k5H1djl.svg)](https://asciinema.org/a/d0ZMZf1Pqw41NodYv6k5H1djl?t=88)

## Redeployment

The best way to upgrade and redeploy Allocator while maintaining your original config and keys is to execute the commands in the script below in order, _in Allocator's directory_ (the commands involve using `sudo rm -rf`, a highly dangerous deletion command, if you're not in the correct directory). Before you begin, make sure you enable the extglob shell option.

The following script is now included in the repository, and is used in the above demonstration. 

```bash
mkdir protected
mv *.ini protected
sudo rm -rf !(protected)  # make sure you have extglob on, and only run this in the Allocator directory!
git clone https://github.com/preritdas/allocator.git
mv allocator/* .
mv protected/* .
sudo rm -rf protected allocator
```

If you'd like a script that not only upgrades Allocator, but rebuilds its dependencies for deployment, create the following script outside of the `allocator` directory. Then, call it when you'd like to upgrade Allocator. The script should exist outside of the directory as it involves cleaning out all files that aren't protected, which will include the script itself. Add the following script to a folder on your PATH. 

```bash
#!/bin/bash

shopt -s extglob  # enable deleting all files except protected

# Upgrades
mkdir protected &&
mv *.ini protected &&
sudo rm -rf !(protected) && 
git clone https://github.com/preritdas/allocator.git &&
mv allocator/* . &&
mv protected/* . &&
sudo rm -rf protected allocator &&


# Deployment
python3.10 -m venv venv &&  # replace with your correct Python 3.10 alias
source venv/bin/activate &&
pip install --upgrade pip &&
pip install -r requirements.txt &&
clear
```

This script will upgrade Allocator and rebuild all dependencies while maintaining your existent config.ini and keys.ini files. 

That said, it's recommended to just use the script built into the repository, `bash scripts/redeploy.sh`, and rebuild dependencies yourself with a virtual environment.

### keys.ini

| Parameter | Type | Behavior | Source |
| --- | --- | --- | --- |
| `Alpaca.API_KEY` | string | Authenticates Alpaca API for trading | Portfolio Dashboard [Alpaca Markets](https://alpaca.markets) |
| `Alpaca.API_SECRET` | string | Authenticates Alpaca API for trading | Portfolio Dashboard [Alpaca Markets](https://alpaca.markets) |
| `Alpaca.BASE_URL` | string | Defines the Alpaca API's endpoint | Portfolio Dashboard [Alpaca Markets](https://alpaca.markets)
| --- | --- | --- | --- |
| `Nexmo.api_key` | string | Authenticates Nexmo for sending text messages | [Nexmo Dashboard](https://dashboard.nexmo.com) |
| `Nexmo.api_secret` | string | Authenticates Nexmo for sending text messages | [Nexmo Dashboard](https://dashboard.nexmo.com) |
| `Nexmo.sender` | string | Specifies which registered Nexmo number to originate text alerts | [Nexmo Dashboard](https://dashboard.nexmo.com)
| --- | --- | --- | --- |
| `Gmail.smtp_host` | string | Necessary for authenticating Gmail to send emails | Default is `'smtp.gmail.com'`. More information [here](https://support.google.com/mail/answer/7126229?hl=en#zippy=%2Cstep-check-that-imap-is-turned-on%2Cstep-change-smtp-other-settings-in-your-email-client). |
| `Gmail.smtp_port` | integer | Necessary for authenticating Gmail to send emails | Default is `465`. More information [here](https://support.google.com/mail/answer/7126229?hl=en#zippy=%2Cstep-check-that-imap-is-turned-on%2Cstep-change-smtp-other-settings-in-your-email-client). |
| `Gmail.email_address` | string | The Gmail _sender's_ address. | The account used to login to Gmail, as the sender. Can be your own email, if you want your reports to come from yourself. |
| `Gmail.password` | string | An _app password_. Gmail has revoked support for 'less-secure apps' so you must enable 2FA and generate an 'app password' instead. | [Google Account Settings](https://myaccount.google.com) |
| --- | --- | --- | --- |
| `User.name` | string | Your name, for daily reports. | Hopefully you remember your name. |
| `User.phone_number` | string | Target phone number for error alerts and daily reports. | Must be in the format `'14258193018'` for U.S. phone numbers. |
| `User.email_address` | string | Target email address for receiving daily reports. | Must be in the format `'youremail@gmail.com'`. |

### config.ini

| Parameter | Behavior | Default |
| --- | --- | --- |
| `rebalance_threshold` | The amount a position must vary from its true proportional value (according to portfolio allocation) in order for Allocator to re-balance it. | 0.01 |
| `portfolio_type` | User selected portfolio according to those specified in the [portfolios](##portfolios) section. | moderate |
| `account_multiplier` | Maintain a portfolio size less or greater (if margin enabled) than your cash balance. | 1 |
| `text_reports` | Choose whether to receive daily reports by text as well as by email. | false |
| `additional_recipients` | Specify a list of emails to which you'd like your reports sent, Do so in the format `additional_recipients = email@gmail.com, email2@me.com` etc. with a comma and space between each email. | '' (empty) |
