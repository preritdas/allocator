"""
Ensure quantities can be properly calculated for allocation.
"""
import allocation


def test_calculate_quantities():
    allocation.calculate_quantities()


def test_reverse_lookup():
    assert allocation.sector_from_etf
