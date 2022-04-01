import alpaca_trade_api as alpaca_api

import _keys

# Instantiate Alpaca API
alpaca = alpaca_api.REST(
    key_id = _keys.alpaca_API_Key,
    secret_key = _keys.alpaca_API_Secret,
    base_url = _keys.alpaca_base_url
)