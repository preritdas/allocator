# Allocator

_Currently, the source code for this project is private. It will be made available once retired for public use. When public, the code will be available on this [GitHub repository](https://github.com/preritdas/allocator)._

----

Allocator is an automated portfolio manager that constantly rebalances holdings to match a pre-defined sectoral division. For example, an allocation in `main.py`'s global parameters might look like:

```python
allocation = {
    "Domestic Large Cap": 0.35,
    "Domestic Mid Cap": 0.05,
    "Domestic Small Cap": 0.02,
    "International": 0.18,
    "Short Term Bonds": 0.12,
    "Aggregate Bonds": 0.28
}
```

Every day, Allocator will read the available cash balance and invest in various ETFs such that the account is exposed to the market in as close to the `allocation` as possible. 

Depositing cash consistently to the account after deployment is _encouraged_ (but not necessary), as this is what gives Allocator the ability to re-invest in all sectors.

Allocator submits several fractional orders to ensure that it can achieve a balance as close as possible to the predefined `allocation`. To ensure rapid execution, when purchases are necessary, allocator will designate the order execution task for each ETF to an independent CPU core. This allows orders to be submitted concurrently and rapidly. 

## Features

All features listed below are functional and have been deployed.

### Automated Investing

Allocator reads the underlying account's cash balance every weekday morning. If there is enough cash to invest in all sectors proportionately (minimum of $1 per sector), it will send and execute orders to do so. Otherwise, it will skip the day and continue with its alert protocol (see Updates section). 

### Allocation Variance

At the end of each week, Allocator will read the underlying account and compare the positions to the optimal `allocation`. It will then calculate the difference between the optimal allocation and true allocation, and text this result to the user (see Updates section). 

### Updates

All alerts and updates are sent to the user by text message (see the necessary files section). Allocator has three rounds of updates.

1. **Execution**: all sectors invested in and their amounts. Or, that there wasn't enough cash to make a round of automatic investments.
2. **Sector Updates**: the daily performance of each sector the account is invested in, and the lifetime performance of the account's positions in this sector. This includes automatic re-investments: the calculation is made using an adjusted cost-basis after any number of re-investments, so its a true representation of the account's net performance in the sector. 
3. **Allocation Variance**: every week, the user is briefed on the success of Allocator's automatic investments. For every sector, they are informed of the variance between the true allocation in the account and the optimal `allocation` defined in Allocator's global parameters. 

Below is a sample of the expected alerts on a given trading day. 

```
(09:35 a.m., market open): Orders have been executed. Bought $35 of VOO, $5 of IJH, $2 of IJR, $18 of IXUS, $12 of ISTB, $23 of AGG, $5 of BTCUSD.

(04:06 p.m., market close): Domestic Large Cap is down 2.23% today. Our position is up 4.15% cumulatively. Domestic Mid Cap is up 1.52% today. Our position is down 2.13% cumulatively. Domestic Small Cap is up 3.14% today. Our position is up 1.53% cumulatively. International is down 0.25% today. Our position is up 1.29% cumulatively. Short Term Bonds is up 0.45% today. Our position is up 0.57% cumulatively. Aggregate bonds is up 0.54% today. Our position is up 0.67% cumulatively. Crypto is down 5.55% today. Our position is up 12.25% cumulatively. 

(04:06 p.m., market close on Friday): In our account, Domestic Large Cap is off by 0.0012%, Domestic Mid Cap is off by 0.0002%, Domestic Small Cap is off by 0.0013%, International is off by 0.00045%, Short Term Bonds is off by 0.0014%, Aggregate Bonds is off by 0.00045%, Crypto is off by 0.014%.
```

## Files

All of these files are necessary for Allocator to function. 

### main.py

The main execution file. Run this file to run Allocator with `python main.py`, using Python 3.10 (developed with Python 3.10.4). Global parameters are modifiable.

```python
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
```

You can designate your own target funds for each sector. 

### texts.py

The primary function of `texts.py` is to define `texts.text_me()`, called in `main.py` when alerting the user. It uses the [Nexmo](https://developer.nexmo.com/api) API and references keys and phone numbers in `_keys.py`. 

### _keys.py

Ensure `_keys.py` contains all the following objects to ensure Allocator runs without errors. 

```python
# Alpaca Keys
alpaca_API_Key = 'alpacaAPIkey'
alpaca_API_Secret = 'alpacaSecretKey'
alpaca_base_url = 'https://api.alpaca.markets'

# Nexmo
nexmo_api_key = 'nexmoKey'
nexmo_api_secret = 'nexmoSecret'
nexmo_sender = 'registeredNumberAsString'
nexmo_my_number = 'userNumberAsString'
```