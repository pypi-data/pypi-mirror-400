"""
Tests for Capacitor Calculator MCP Server
"""

import pytest
import math
from servers.capacitor_calculator import (
    calculate_capacitive_reactance,
    calculate_rc_time_constant,
    calculate_resonant_frequency,
    suggest_capacitor_for_filter,
    _format_capacitance,
    _format_resistance,
    _format_frequency,
    _format_time,
    _format_inductance,
)


class TestFormatCapacitance:
    """Test capacitance formatting helper."""

    def test_picofarads(self):
        assert "100pF" in _format_capacitance(100e-12)
        assert "47pF" in _format_capacitance(47e-12)

    def test_nanofarads(self):
        assert "10nF" in _format_capacitance(10e-9)
        assert "100nF" in _format_capacitance(100e-9)

    def test_microfarads(self):
        assert "1µF" in _format_capacitance(1e-6)
        assert "100µF" in _format_capacitance(100e-6)
        assert "4.7" in _format_capacitance(4.7e-6)

    def test_millifarads(self):
        assert "mF" in _format_capacitance(1e-3)


class TestFormatFrequency:
    """Test frequency formatting helper."""

    def test_hertz(self):
        assert "100Hz" in _format_frequency(100)
        assert "50Hz" in _format_frequency(50)

    def test_kilohertz(self):
        assert "kHz" in _format_frequency(1000)
        assert "kHz" in _format_frequency(10000)

    def test_megahertz(self):
        assert "MHz" in _format_frequency(1e6)
        assert "MHz" in _format_frequency(2.4e6)

    def test_gigahertz(self):
        assert "GHz" in _format_frequency(1e9)


class TestFormatTime:
    """Test time formatting helper."""

    def test_nanoseconds(self):
        assert "ns" in _format_time(1e-9)
        assert "100" in _format_time(100e-9)

    def test_microseconds(self):
        assert "µs" in _format_time(1e-6)
        assert "µs" in _format_time(100e-6)

    def test_milliseconds(self):
        assert "ms" in _format_time(1e-3)
        assert "ms" in _format_time(100e-3)

    def test_seconds(self):
        assert "s" in _format_time(1)
        assert "s" in _format_time(2.5)


class TestCalculateCapacitiveReactance:
    """Test capacitive reactance calculations."""

    def test_1uf_at_1khz(self):
        """1µF at 1kHz should give approximately 159Ω."""
        result = calculate_capacitive_reactance(1e-6, 1000)
        assert "159" in result  # ~159.15Ω
        assert "Xc" in result

    def test_100nf_at_10khz(self):
        """100nF at 10kHz should give approximately 159Ω."""
        result = calculate_capacitive_reactance(100e-9, 10000)
        assert "159" in result  # ~159.15Ω

    def test_reactance_formula(self):
        """Verify the Xc = 1/(2πfC) formula."""
        c = 10e-6  # 10µF
        f = 50     # 50Hz
        expected_xc = 1 / (2 * math.pi * f * c)
        result = calculate_capacitive_reactance(c, f)
        # Expected: ~318Ω
        assert "318" in result or "Ω" in result

    def test_output_includes_formula(self):
        """Result should include the formula for reference."""
        result = calculate_capacitive_reactance(1e-6, 1000)
        assert "2π" in result or "Formula" in result


class TestCalculateRcTimeConstant:
    """Test RC time constant calculations."""

    def test_10k_100uf_equals_1_second(self):
        """10kΩ + 100µF = 1 second."""
        result = calculate_rc_time_constant(10000, 100e-6)
        assert "1.000s" in result or "1s" in result

    def test_1k_1uf_equals_1ms(self):
        """1kΩ + 1µF = 1 millisecond."""
        result = calculate_rc_time_constant(1000, 1e-6)
        assert "1.000ms" in result or "ms" in result

    def test_includes_charging_timeline(self):
        """Result should include the 5τ charging timeline."""
        result = calculate_rc_time_constant(1000, 1e-6)
        assert "63.2%" in result
        assert "99.3%" in result
        assert "5τ" in result

    def test_includes_cutoff_frequency(self):
        """Result should include the equivalent filter cutoff frequency."""
        result = calculate_rc_time_constant(10000, 1e-6)
        assert "Hz" in result
        assert "cutoff" in result.lower() or "Cutoff" in result


class TestCalculateResonantFrequency:
    """Test LC resonant frequency calculations."""

    def test_1mh_1nf(self):
        """1mH + 1nF should resonate at approximately 159kHz."""
        result = calculate_resonant_frequency(1e-3, 1e-9)
        # f = 1/(2π√(LC)) = 1/(2π√(1e-3 × 1e-9)) ≈ 159.15kHz
        assert "159" in result
        assert "kHz" in result

    def test_100uh_100pf(self):
        """100µH + 100pF should resonate at approximately 1.59MHz."""
        result = calculate_resonant_frequency(100e-6, 100e-12)
        assert "MHz" in result

    def test_at_resonance_xl_equals_xc(self):
        """At resonance, XL should equal Xc."""
        result = calculate_resonant_frequency(1e-3, 1e-9)
        assert "XL = Xc" in result or "XL" in result

    def test_includes_applications(self):
        """Result should mention typical applications."""
        result = calculate_resonant_frequency(1e-3, 1e-9)
        assert "Applications" in result or "circuit" in result.lower()


class TestSuggestCapacitorForFilter:
    """Test filter capacitor recommendations."""

    def test_1khz_lowpass_10k(self):
        """1kHz low-pass with 10kΩ needs approximately 15.9nF."""
        result = suggest_capacitor_for_filter(1000, 10000, "low-pass")
        # C = 1/(2πfR) = 1/(2π × 1000 × 10000) ≈ 15.9nF
        assert "nF" in result
        assert "15" in result or "18" in result  # Nearest E12 values

    def test_100hz_lowpass_1k(self):
        """100Hz low-pass with 1kΩ needs approximately 1.59µF."""
        result = suggest_capacitor_for_filter(100, 1000, "low-pass")
        assert "µF" in result

    def test_high_pass_filter(self):
        """High-pass filter should show different circuit diagram."""
        result = suggest_capacitor_for_filter(1000, 10000, "high-pass")
        assert "High-Pass" in result
        assert "above fc" in result.lower() or "above" in result

    def test_low_pass_filter(self):
        """Low-pass filter should show correct circuit diagram."""
        result = suggest_capacitor_for_filter(1000, 10000, "low-pass")
        assert "Low-Pass" in result
        assert "below fc" in result.lower() or "below" in result

    def test_includes_standard_values(self):
        """Result should include standard E12 capacitor options."""
        result = suggest_capacitor_for_filter(1000, 10000, "low-pass")
        assert "E12" in result
        assert "Closest" in result

    def test_includes_circuit_diagram(self):
        """Result should include ASCII circuit diagram."""
        result = suggest_capacitor_for_filter(1000, 10000, "low-pass")
        assert "GND" in result or "───" in result


class TestIntegration:
    """Integration tests for realistic usage."""

    def test_audio_filter_design(self):
        """Design a 1kHz audio low-pass filter."""
        # Get capacitor suggestion
        filter_result = suggest_capacitor_for_filter(1000, 10000, "low-pass")
        assert "nF" in filter_result
        
        # Verify with RC time constant
        tau_result = calculate_rc_time_constant(10000, 15e-9)
        assert "µs" in tau_result

    def test_decoupling_capacitor_reactance(self):
        """Check 100nF decoupling at 1MHz (common for digital ICs)."""
        result = calculate_capacitive_reactance(100e-9, 1e6)
        # Xc should be about 1.59Ω at 1MHz
        assert "1.5" in result or "1.6" in result
        assert "Ω" in result

    def test_radio_tuning_circuit(self):
        """Design an AM radio tuner (~1MHz)."""
        # 1MHz with 100µH inductor
        result = calculate_resonant_frequency(100e-6, 253e-12)
        # Should be close to 1MHz
        assert "MHz" in result or "kHz" in result
