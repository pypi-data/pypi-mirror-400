"""
Capacitor Calculator MCP Server
===============================
Calculate capacitive reactance, RC time constants, resonant frequency, and filter design.

Transport: stdio (default)
Tools:
  - calculate_capacitive_reactance: Xc = 1 / (2πfC)
  - calculate_rc_time_constant: τ = R × C
  - calculate_resonant_frequency: f = 1 / (2π√LC)
  - suggest_capacitor_for_filter: Recommend capacitor for RC low-pass filter
"""

import math
from typing import Annotated, Literal
from pydantic import Field
from mcp.server.fastmcp import FastMCP

# === Server Initialization ===
mcp = FastMCP(
    name="Capacitor Calculator",
    instructions=(
        "A tool for electronics engineers to perform capacitor-related calculations. "
        "Supports capacitive reactance, RC time constants, LC resonant frequency, "
        "and RC filter design recommendations."
    ),
)

# === Standard Capacitor Values (E12 series in Farads) ===
E12_CAPACITOR_VALUES = [
    # picofarads (1e-12)
    1e-12, 1.2e-12, 1.5e-12, 1.8e-12, 2.2e-12, 2.7e-12,
    3.3e-12, 3.9e-12, 4.7e-12, 5.6e-12, 6.8e-12, 8.2e-12,
    10e-12, 12e-12, 15e-12, 18e-12, 22e-12, 27e-12,
    33e-12, 39e-12, 47e-12, 56e-12, 68e-12, 82e-12,
    100e-12, 120e-12, 150e-12, 180e-12, 220e-12, 270e-12,
    330e-12, 390e-12, 470e-12, 560e-12, 680e-12, 820e-12,
    # nanofarads (1e-9)
    1e-9, 1.2e-9, 1.5e-9, 1.8e-9, 2.2e-9, 2.7e-9,
    3.3e-9, 3.9e-9, 4.7e-9, 5.6e-9, 6.8e-9, 8.2e-9,
    10e-9, 12e-9, 15e-9, 18e-9, 22e-9, 27e-9,
    33e-9, 39e-9, 47e-9, 56e-9, 68e-9, 82e-9,
    100e-9, 120e-9, 150e-9, 180e-9, 220e-9, 270e-9,
    330e-9, 390e-9, 470e-9, 560e-9, 680e-9, 820e-9,
    # microfarads (1e-6)
    1e-6, 2.2e-6, 3.3e-6, 4.7e-6, 6.8e-6, 10e-6,
    22e-6, 33e-6, 47e-6, 68e-6, 100e-6, 220e-6,
    330e-6, 470e-6, 680e-6, 1000e-6,
]


def _format_capacitance(farads: float) -> str:
    """Format capacitance with appropriate unit (pF, nF, µF, mF)."""
    if farads >= 1e-3:
        return f"{farads * 1e3:.2f}mF"
    elif farads >= 1e-6:
        value = farads * 1e6
        if value == int(value):
            return f"{int(value)}µF"
        return f"{value:.2f}µF"
    elif farads >= 1e-9:
        value = farads * 1e9
        if value == int(value):
            return f"{int(value)}nF"
        return f"{value:.2f}nF"
    else:
        value = farads * 1e12
        if value == int(value):
            return f"{int(value)}pF"
        return f"{value:.2f}pF"


def _format_resistance(ohms: float) -> str:
    """Format resistance with appropriate unit (Ω, kΩ, MΩ)."""
    if ohms >= 1e6:
        return f"{ohms / 1e6:.2f}MΩ"
    elif ohms >= 1e3:
        value = ohms / 1e3
        if value == int(value):
            return f"{int(value)}kΩ"
        return f"{value:.2f}kΩ"
    else:
        if ohms == int(ohms):
            return f"{int(ohms)}Ω"
        return f"{ohms:.2f}Ω"


def _format_frequency(hz: float) -> str:
    """Format frequency with appropriate unit (Hz, kHz, MHz, GHz)."""
    if hz >= 1e9:
        return f"{hz / 1e9:.2f}GHz"
    elif hz >= 1e6:
        return f"{hz / 1e6:.2f}MHz"
    elif hz >= 1e3:
        return f"{hz / 1e3:.2f}kHz"
    else:
        if hz == int(hz):
            return f"{int(hz)}Hz"
        return f"{hz:.2f}Hz"


def _format_time(seconds: float) -> str:
    """Format time with appropriate unit (ns, µs, ms, s)."""
    if seconds >= 1:
        return f"{seconds:.3f}s"
    elif seconds >= 1e-3:
        return f"{seconds * 1e3:.3f}ms"
    elif seconds >= 1e-6:
        return f"{seconds * 1e6:.3f}µs"
    else:
        return f"{seconds * 1e9:.3f}ns"


def _format_inductance(henries: float) -> str:
    """Format inductance with appropriate unit (nH, µH, mH, H)."""
    if henries >= 1:
        return f"{henries:.3f}H"
    elif henries >= 1e-3:
        return f"{henries * 1e3:.3f}mH"
    elif henries >= 1e-6:
        return f"{henries * 1e6:.3f}µH"
    else:
        return f"{henries * 1e9:.3f}nH"


# === Tools ===
@mcp.tool()
def calculate_capacitive_reactance(
    capacitance_farads: Annotated[float, Field(description="Capacitance in Farads (e.g., 1e-6 for 1µF, 100e-12 for 100pF)", gt=0)],
    frequency_hz: Annotated[float, Field(description="Frequency in Hertz (e.g., 1000 for 1kHz)", gt=0)],
) -> str:
    """
    Calculate capacitive reactance (Xc) at a given frequency.
    
    Formula: Xc = 1 / (2π × f × C)
    
    Capacitive reactance represents the opposition to AC current flow through a capacitor.
    It decreases as frequency increases (capacitors pass high frequencies more easily).
    
    Examples:
        1µF at 1kHz → Xc ≈ 159Ω
        100nF at 10kHz → Xc ≈ 159Ω
    """
    xc = 1 / (2 * math.pi * frequency_hz * capacitance_farads)
    
    # Calculate current at 1V for reference
    current_at_1v = 1 / xc  # I = V/Xc
    
    return f"""⚡ Capacitive Reactance Calculator

**Input:**
  • Capacitance: {_format_capacitance(capacitance_farads)}
  • Frequency: {_format_frequency(frequency_hz)}

**Result:**
  • Reactance (Xc) = **{_format_resistance(xc)}**
  • Current at 1Vac = {current_at_1v * 1000:.3f}mA

**Formula:** Xc = 1 / (2π × f × C)

**Insight:** At this frequency, the capacitor behaves like a {_format_resistance(xc)} resistor for AC signals."""


@mcp.tool()
def calculate_rc_time_constant(
    resistance_ohms: Annotated[float, Field(description="Resistance in Ohms (e.g., 10000 for 10kΩ)", gt=0)],
    capacitance_farads: Annotated[float, Field(description="Capacitance in Farads (e.g., 1e-6 for 1µF)", gt=0)],
) -> str:
    """
    Calculate RC circuit time constant (τ = R × C).
    
    The time constant τ represents:
    - Time to charge to ~63.2% of final voltage
    - Time to discharge to ~36.8% of initial voltage
    - 5τ ≈ 99.3% of final value (considered "fully" charged/discharged)
    
    Examples:
        10kΩ + 100µF → τ = 1 second
        1kΩ + 1µF → τ = 1 millisecond
    """
    tau = resistance_ohms * capacitance_farads
    
    # Calculate key timing milestones
    t_63 = tau          # 63.2% charge
    t_86 = 2 * tau      # 86.5% charge
    t_95 = 3 * tau      # 95.0% charge
    t_98 = 4 * tau      # 98.2% charge
    t_99 = 5 * tau      # 99.3% charge
    
    # Calculate cutoff frequency for this RC combination
    fc = 1 / (2 * math.pi * tau)
    
    return f"""⏱️ RC Time Constant Calculator

**Input:**
  • Resistance: {_format_resistance(resistance_ohms)}
  • Capacitance: {_format_capacitance(capacitance_farads)}

**Time Constant:**
  • τ (tau) = **{_format_time(tau)}**

**Charging Timeline:**
  • 1τ ({_format_time(t_63)}): 63.2% charged
  • 2τ ({_format_time(t_86)}): 86.5% charged
  • 3τ ({_format_time(t_95)}): 95.0% charged
  • 4τ ({_format_time(t_98)}): 98.2% charged
  • 5τ ({_format_time(t_99)}): 99.3% charged ✓

**As Low-Pass Filter:**
  • Cutoff frequency (-3dB): {_format_frequency(fc)}

**Formula:** τ = R × C"""


@mcp.tool()
def calculate_resonant_frequency(
    inductance_henries: Annotated[float, Field(description="Inductance in Henries (e.g., 1e-3 for 1mH, 100e-6 for 100µH)", gt=0)],
    capacitance_farads: Annotated[float, Field(description="Capacitance in Farads (e.g., 1e-9 for 1nF)", gt=0)],
) -> str:
    """
    Calculate LC resonant frequency.
    
    Formula: f = 1 / (2π√(LC))
    
    At resonance:
    - Inductive reactance (XL) equals capacitive reactance (Xc)
    - Impedance is at minimum (series) or maximum (parallel)
    - Used in tuned circuits, filters, oscillators
    
    Examples:
        1mH + 1nF → f ≈ 159kHz
        100µH + 100pF → f ≈ 1.59MHz
    """
    f_resonant = 1 / (2 * math.pi * math.sqrt(inductance_henries * capacitance_farads))
    
    # Calculate reactances at resonance
    xl = 2 * math.pi * f_resonant * inductance_henries
    xc = 1 / (2 * math.pi * f_resonant * capacitance_farads)
    
    # Calculate characteristic impedance (Z0 = √(L/C))
    z0 = math.sqrt(inductance_henries / capacitance_farads)
    
    return f"""🔊 LC Resonant Frequency Calculator

**Input:**
  • Inductance: {_format_inductance(inductance_henries)}
  • Capacitance: {_format_capacitance(capacitance_farads)}

**Resonant Frequency:**
  • f₀ = **{_format_frequency(f_resonant)}**

**At Resonance:**
  • XL = Xc = {_format_resistance(xl)}
  • Characteristic Impedance (Z₀) = {_format_resistance(z0)}

**Formula:** f = 1 / (2π√(LC))

**Applications:**
  • Radio tuning circuits
  • Band-pass/band-stop filters
  • Oscillator tank circuits"""


@mcp.tool()
def suggest_capacitor_for_filter(
    cutoff_frequency_hz: Annotated[float, Field(description="Target cutoff frequency in Hz (-3dB point)", gt=0)],
    resistance_ohms: Annotated[float, Field(description="Filter resistance in Ohms (e.g., 10000 for 10kΩ)", gt=0)],
    filter_type: Annotated[Literal["low-pass", "high-pass"], Field(description="Filter type: 'low-pass' or 'high-pass'")] = "low-pass",
) -> str:
    """
    Recommend capacitor value for an RC filter design.
    
    For a given cutoff frequency and resistance, calculates the required
    capacitance and suggests the nearest standard E12 series value.
    
    Formula: C = 1 / (2π × f × R)
    
    Examples:
        1kHz cutoff with 10kΩ → C ≈ 15.9nF (use 15nF or 18nF)
        100Hz cutoff with 1kΩ → C ≈ 1.59µF (use 1.5µF or 2.2µF)
    """
    # Calculate exact capacitance needed
    c_exact = 1 / (2 * math.pi * cutoff_frequency_hz * resistance_ohms)
    
    # Find nearest standard values
    E12_CAPACITOR_VALUES.sort()
    closest = min(E12_CAPACITOR_VALUES, key=lambda c: abs(c - c_exact))
    closest_idx = E12_CAPACITOR_VALUES.index(closest)
    
    # Get nearby options
    options = []
    for i in range(max(0, closest_idx - 2), min(len(E12_CAPACITOR_VALUES), closest_idx + 3)):
        c = E12_CAPACITOR_VALUES[i]
        actual_fc = 1 / (2 * math.pi * c * resistance_ohms)
        diff_pct = ((actual_fc - cutoff_frequency_hz) / cutoff_frequency_hz) * 100
        options.append((c, actual_fc, diff_pct, i == closest_idx))
    
    # Calculate time constant and reactance at cutoff
    tau = resistance_ohms * c_exact
    xc_at_fc = resistance_ohms  # At cutoff, Xc = R
    
    # Build result
    result = f"""🎛️ RC Filter Capacitor Selector

**Design Requirements:**
  • Filter Type: {filter_type.replace('-', ' ').title()}
  • Cutoff Frequency: {_format_frequency(cutoff_frequency_hz)}
  • Resistance: {_format_resistance(resistance_ohms)}

**Calculated Capacitance:**
  • Exact: {_format_capacitance(c_exact)} ({c_exact:.3e}F)
  • Reactance at fc: {_format_resistance(xc_at_fc)}
  • Time Constant: {_format_time(tau)}

**Recommended Standard Values (E12):**"""
    
    for c, fc, diff, is_best in options:
        marker = " ← Closest" if is_best else ""
        result += f"\n  • {_format_capacitance(c):>8} → fc = {_format_frequency(fc)} ({diff:+.1f}%){marker}"
    
    # Add circuit diagram
    if filter_type == "low-pass":
        result += """

**Circuit (Low-Pass):**
```
    R
Vin ───/\\/\\/──┬─── Vout
              │
              ┴ C
              │
             GND
```
Passes: Frequencies below fc
Attenuates: Frequencies above fc"""
    else:
        result += """

**Circuit (High-Pass):**
```
    C
Vin ───||────┬─── Vout
             │
             R
             │
            GND
```
Passes: Frequencies above fc
Attenuates: Frequencies below fc"""
    
    result += f"""

**Formula:** C = 1 / (2π × f × R)"""
    
    return result


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
