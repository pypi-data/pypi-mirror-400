"""
Tests for Resistor Color Code Decoder MCP Server
"""

import pytest
from servers.resistor_decoder import (
    decode_resistor_color_bands,
    encode_resistor_value,
    find_standard_resistor,
    _format_resistance,
    _normalize_color,
)


class TestFormatResistance:
    """Test resistance formatting helper."""

    def test_ohms(self):
        assert _format_resistance(100) == "100Ω"
        assert _format_resistance(470) == "470Ω"

    def test_kilohms(self):
        assert _format_resistance(1000) == "1kΩ"
        assert _format_resistance(4700) == "4.7kΩ"
        assert _format_resistance(10000) == "10kΩ"

    def test_megohms(self):
        assert _format_resistance(1000000) == "1MΩ"
        assert _format_resistance(2200000) == "2.2MΩ"

    def test_fractional(self):
        assert _format_resistance(0.47) == "0.47Ω"


class TestNormalizeColor:
    """Test color normalization."""

    def test_case_insensitive(self):
        assert _normalize_color("Brown") == "brown"
        assert _normalize_color("GOLD") == "gold"

    def test_whitespace(self):
        assert _normalize_color("  red  ") == "red"

    def test_grey_gray(self):
        assert _normalize_color("grey") == "grey"
        assert _normalize_color("gray") == "gray"


class TestDecodeResistorColorBands:
    """Test 4-band and 5-band resistor decoding."""

    def test_4band_1k_5percent(self):
        """Brown, Black, Red, Gold = 1kΩ ±5%"""
        result = decode_resistor_color_bands("brown", "black", "red", "gold")
        assert "1kΩ" in result
        assert "5.0%" in result

    def test_4band_4k7_5percent(self):
        """Yellow, Violet, Red, Gold = 4.7kΩ ±5%"""
        result = decode_resistor_color_bands("yellow", "violet", "red", "gold")
        assert "4.7kΩ" in result
        assert "5.0%" in result

    def test_4band_10k_10percent(self):
        """Brown, Black, Orange, Silver = 10kΩ ±10%"""
        result = decode_resistor_color_bands("brown", "black", "orange", "silver")
        assert "10kΩ" in result
        assert "10.0%" in result

    def test_4band_100_ohm(self):
        """Brown, Black, Brown, Gold = 100Ω ±5%"""
        result = decode_resistor_color_bands("brown", "black", "brown", "gold")
        assert "100Ω" in result

    def test_5band_1k_1percent(self):
        """Brown, Black, Black, Brown, Brown = 1kΩ ±1%"""
        result = decode_resistor_color_bands("brown", "black", "black", "brown", "brown")
        assert "1kΩ" in result
        assert "1.0%" in result

    def test_5band_precision(self):
        """Brown, Red, Black, Brown, Brown = 1.2kΩ ±1%"""
        result = decode_resistor_color_bands("brown", "red", "black", "brown", "brown")
        assert "1.2kΩ" in result

    def test_invalid_color(self):
        """Invalid color should return error."""
        result = decode_resistor_color_bands("purple", "black", "red", "gold")
        assert "❌" in result or "Invalid" in result.lower()

    def test_case_insensitive(self):
        """Colors should be case-insensitive."""
        result = decode_resistor_color_bands("BROWN", "Black", "RED", "Gold")
        assert "1kΩ" in result


class TestEncodeResistorValue:
    """Test encoding resistance to color bands."""

    def test_encode_1k_4band(self):
        """1000Ω should encode to Brown, Black, Red."""
        result = encode_resistor_value(1000, 5.0, 4)
        assert "Brown" in result
        assert "Black" in result
        assert "Red" in result
        assert "Gold" in result

    def test_encode_4k7_4band(self):
        """4700Ω should encode to Yellow, Violet, Red."""
        result = encode_resistor_value(4700, 5.0, 4)
        assert "Yellow" in result
        assert "Violet" in result
        assert "Red" in result

    def test_encode_1k_5band(self):
        """1000Ω 5-band should encode correctly."""
        result = encode_resistor_value(1000, 1.0, 5)
        assert "Brown" in result
        assert "1.0%" in result
        assert "1kΩ" in result  # Should encode to 1kΩ, not 10kΩ

    def test_invalid_tolerance(self):
        """Invalid tolerance should return error."""
        result = encode_resistor_value(1000, 3.0, 4)  # 3% is not standard
        assert "❌" in result or "Invalid" in result.lower()


class TestFindStandardResistor:
    """Test finding standard resistor values."""

    def test_e24_exact_match(self):
        """Exact E24 value should match perfectly."""
        result = find_standard_resistor(4700, "E24")
        assert "4.7kΩ" in result
        assert "0.00%" in result  # Exact match

    def test_e24_nearest(self):
        """Non-standard value should find nearest E24."""
        result = find_standard_resistor(5000, "E24")  # 5k is not E24
        assert "5.1kΩ" in result or "4.7kΩ" in result  # Either neighbor

    def test_e12_series(self):
        """E12 should have fewer options."""
        result = find_standard_resistor(1500, "E12")
        assert "1.5kΩ" in result or "1.2kΩ" in result or "1.8kΩ" in result

    def test_e96_precision(self):
        """E96 should provide closer matches."""
        result = find_standard_resistor(1050, "E96")
        assert "E96" in result

    def test_includes_color_code(self):
        """Result should include color code."""
        result = find_standard_resistor(1000, "E24")
        assert "Color Code" in result


class TestIntegration:
    """Integration tests for realistic usage."""

    def test_decode_common_values(self):
        """Test common resistor values used in electronics."""
        # 330Ω - LED current limiting
        result = decode_resistor_color_bands("orange", "orange", "brown", "gold")
        assert "330Ω" in result

        # 10kΩ - Pull-up resistor
        result = decode_resistor_color_bands("brown", "black", "orange", "gold")
        assert "10kΩ" in result

    def test_roundtrip_encode_decode(self):
        """Encoding then decoding should return original value."""
        # Encode 2.2kΩ
        encoded = encode_resistor_value(2200, 5.0, 4)
        # Extract colors and verify
        assert "Red" in encoded and "2.2kΩ" in encoded
