# Non-local imports
import alpaca_trade_api

# Project modules
import _keys


# Instantiate Alpaca API
alpaca = alpaca_trade_api.REST(
    key_id = _keys.Alpaca.API_KEY,
    secret_key = _keys.Alpaca.API_SECRET,
    base_url = _keys.Alpaca.BASE_URL
)


# Ideal allocations
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

etf_allocation = {etf: alloc for etf in etfs.values() for alloc in allocation.values()}


def _current_positions() -> dict[str, float]:
    return {etf: float(alpaca.get_position(etf).market_value) for etf in etfs.values()}


def positional_deltas() -> dict[str, float]:
    account_total = float(alpaca.get_account().equity)
    positions = _current_positions()

    ideal_alloc = {}
    for etf, alloc, in zip(etfs.values(), allocation.values()):
        ideal_alloc[etf] = alloc * account_total

    return_deltas = {}
    for position in positions:
        return_deltas[position] = round((positions[position] - ideal_alloc[position]), 2)

    return return_deltas


def correct_deltas() -> None:
    """Places orders."""
    deltas = positional_deltas()

    for position in deltas:
        if deltas[position] >= 5:
            print("")
            print(position, deltas[position])
            print(f"Selling {deltas[position]} dollars of {position}.")

            # Do it
            alpaca.submit_order(
                symbol = position,
                side = 'sell',
                notional = deltas[position]
            )
        elif deltas[position] < -5:
            print("")
            print(position, deltas[position])
            print(f"Buying {deltas[position]} dollars of {position}.")

            # Do it
            alpaca.submit_order(
                symbol = position,
                side = 'buy',
                notional = deltas[position] * -1
            )


if __name__ == '__main__':
    correct_deltas()
