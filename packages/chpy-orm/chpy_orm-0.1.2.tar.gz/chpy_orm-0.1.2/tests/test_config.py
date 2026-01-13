"""
Tests for chpy.config module.
"""

import pytest
from chpy.config import (
    EXCHANGES,
    EXCHANGE_BASE_CURRENCIES,
    EXCHANGE_CURRENCIES,
    get_exchange_pairs,
    is_valid_pair,
    get_all_pairs,
)


class TestConfig:
    """Test cases for config module."""
    
    def test_exchanges_list(self):
        """Test EXCHANGES is a list."""
        assert isinstance(EXCHANGES, list)
        assert len(EXCHANGES) > 0
        assert "BINANCE" in EXCHANGES
        assert "KUCOIN" in EXCHANGES
    
    def test_exchange_base_currencies_dict(self):
        """Test EXCHANGE_BASE_CURRENCIES structure."""
        assert isinstance(EXCHANGE_BASE_CURRENCIES, dict)
        assert "BINANCE" in EXCHANGE_BASE_CURRENCIES
        assert isinstance(EXCHANGE_BASE_CURRENCIES["BINANCE"], list)
        assert "USDT" in EXCHANGE_BASE_CURRENCIES["BINANCE"]
    
    def test_exchange_currencies_dict(self):
        """Test EXCHANGE_CURRENCIES structure."""
        assert isinstance(EXCHANGE_CURRENCIES, dict)
        assert "BINANCE" in EXCHANGE_CURRENCIES
        assert isinstance(EXCHANGE_CURRENCIES["BINANCE"], list)
        assert len(EXCHANGE_CURRENCIES["BINANCE"]) > 0
        assert "BTC" in EXCHANGE_CURRENCIES["BINANCE"]
        assert "ETH" in EXCHANGE_CURRENCIES["BINANCE"]
    
    def test_get_exchange_pairs_binance(self):
        """Test get_exchange_pairs for BINANCE."""
        pairs = get_exchange_pairs("BINANCE")
        
        assert isinstance(pairs, list)
        assert len(pairs) > 0
        assert "BTC-USDT" in pairs
        assert "ETH-USDT" in pairs
        # Should not have IRT pairs for BINANCE (only USDT)
        # Check if pair ends with "-IRT" to avoid false positives like "VIRTUAL-USDT"
        irt_pairs = [pair for pair in pairs if pair.endswith("-IRT")]
        assert len(irt_pairs) == 0, f"BINANCE should not have IRT pairs, but found: {irt_pairs[:5]}"
    
    def test_get_exchange_pairs_nobitex(self):
        """Test get_exchange_pairs for NOBITEX."""
        pairs = get_exchange_pairs("NOBITEX")
        
        assert isinstance(pairs, list)
        assert len(pairs) > 0
        # NOBITEX should have both USDT and IRT pairs
        assert any("USDT" in pair for pair in pairs)
        assert any("IRT" in pair for pair in pairs)
    
    def test_get_exchange_pairs_case_insensitive(self):
        """Test get_exchange_pairs is case-insensitive."""
        pairs_upper = get_exchange_pairs("BINANCE")
        pairs_lower = get_exchange_pairs("binance")
        pairs_mixed = get_exchange_pairs("Binance")
        
        assert pairs_upper == pairs_lower == pairs_mixed
    
    def test_get_exchange_pairs_invalid(self):
        """Test get_exchange_pairs with invalid exchange."""
        pairs = get_exchange_pairs("INVALID_EXCHANGE")
        assert pairs == []
    
    def test_is_valid_pair_valid(self):
        """Test is_valid_pair with valid pairs."""
        assert is_valid_pair("BTC-USDT") is True
        assert is_valid_pair("ETH-USDT") is True
        assert is_valid_pair("BTC-IRT") is True
    
    def test_is_valid_pair_invalid_format(self):
        """Test is_valid_pair with invalid formats."""
        assert is_valid_pair("BTCUSDT") is False  # Missing dash
        assert is_valid_pair("BTC") is False  # No base currency
        assert is_valid_pair("") is False  # Empty string
        assert is_valid_pair("BTC-") is False  # Missing base
        assert is_valid_pair("-USDT") is False  # Missing currency
    
    def test_is_valid_pair_with_exchange(self):
        """Test is_valid_pair with specific exchange."""
        assert is_valid_pair("BTC-USDT", "BINANCE") is True
        assert is_valid_pair("BTC-USDT", "KUCOIN") is True
        # BINANCE doesn't support IRT
        assert is_valid_pair("BTC-IRT", "BINANCE") is False
        # NOBITEX supports IRT
        assert is_valid_pair("BTC-IRT", "NOBITEX") is True
    
    def test_is_valid_pair_with_exchange_case_insensitive(self):
        """Test is_valid_pair exchange parameter is case-insensitive."""
        assert is_valid_pair("BTC-USDT", "BINANCE") == is_valid_pair("BTC-USDT", "binance")
        assert is_valid_pair("BTC-USDT", "BINANCE") == is_valid_pair("BTC-USDT", "Binance")
    
    def test_is_valid_pair_with_invalid_exchange(self):
        """Test is_valid_pair with invalid exchange."""
        assert is_valid_pair("BTC-USDT", "INVALID") is False
    
    def test_is_valid_pair_with_exchange_invalid_currency(self):
        """Test is_valid_pair with exchange but invalid currency for that exchange."""
        # Use a currency that doesn't exist in BINANCE
        assert is_valid_pair("INVALIDCURRENCY-USDT", "BINANCE") is False
    
    def test_is_valid_pair_with_exchange_invalid_base(self):
        """Test is_valid_pair with exchange but invalid base for that exchange."""
        # BINANCE doesn't support IRT as base
        assert is_valid_pair("BTC-INVALIDBASE", "BINANCE") is False
    
    def test_is_valid_pair_no_exchange_invalid_currency(self):
        """Test is_valid_pair without exchange for invalid currency."""
        assert is_valid_pair("INVALIDCURRENCY-USDT") is False
    
    def test_is_valid_pair_no_exchange_invalid_base(self):
        """Test is_valid_pair without exchange for invalid base."""
        assert is_valid_pair("BTC-INVALIDBASE") is False
    
    def test_is_valid_pair_multiple_dashes(self):
        """Test is_valid_pair with multiple dashes (should use first dash only)."""
        # split("-", 1) will split only on first dash
        # So "BTC-USD-T" will be split as ["BTC", "USD-T"]
        # This should be invalid as "USD-T" is not a valid base
        assert is_valid_pair("BTC-USD-T") is False
    
    def test_get_all_pairs(self):
        """Test get_all_pairs function."""
        pairs = get_all_pairs()
        
        assert isinstance(pairs, list)
        assert len(pairs) > 0
        assert "BTC-USDT" in pairs
        assert "ETH-USDT" in pairs
        # Should be sorted
        assert pairs == sorted(pairs)
        # Should have no duplicates
        assert len(pairs) == len(set(pairs))
    
    def test_get_all_pairs_includes_all_exchanges(self):
        """Test get_all_pairs includes pairs from all exchanges."""
        pairs = get_all_pairs()
        
        # Should have USDT pairs (from BINANCE, KUCOIN, etc.)
        assert any("USDT" in pair for pair in pairs)
        # Should have IRT pairs (from NOBITEX, BITPIN, WALLEX)
        assert any("IRT" in pair for pair in pairs)
    
    def test_exchange_consistency(self):
        """Test that all exchanges in EXCHANGES have currency definitions."""
        for exchange in EXCHANGES:
            assert exchange in EXCHANGE_CURRENCIES, f"{exchange} missing from EXCHANGE_CURRENCIES"
            assert exchange in EXCHANGE_BASE_CURRENCIES, f"{exchange} missing from EXCHANGE_BASE_CURRENCIES"
            assert len(EXCHANGE_CURRENCIES[exchange]) > 0, f"{exchange} has no currencies"
            assert len(EXCHANGE_BASE_CURRENCIES[exchange]) > 0, f"{exchange} has no base currencies"
    
    def test_pair_generation(self):
        """Test that pairs are correctly generated from currencies and bases."""
        binance_pairs = get_exchange_pairs("BINANCE")
        binance_currencies = EXCHANGE_CURRENCIES["BINANCE"]
        binance_bases = EXCHANGE_BASE_CURRENCIES["BINANCE"]
        
        # Every pair should be currency-base format
        for pair in binance_pairs:
            parts = pair.split("-")
            assert len(parts) == 2
            currency, base = parts
            assert currency in binance_currencies
            assert base in binance_bases
        
        # Should have correct number of pairs
        expected_count = len(binance_currencies) * len(binance_bases)
        assert len(binance_pairs) == expected_count

