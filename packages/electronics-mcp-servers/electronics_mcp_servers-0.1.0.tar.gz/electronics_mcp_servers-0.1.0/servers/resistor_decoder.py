"""
Resistor Color Code Decoder MCP Server
======================================
Decode/encode resistor color bands and find standard resistor values.

Transport: stdio (default)
Tools:
  - decode_resistor_color_bands: Decode 4-band or 5-band resistor color codes
  - encode_resistor_value: Get color bands for a given resistance value
  - find_standard_resistor: Find nearest standard resistor value (E12/E24/E96)
"""

from typing import Annotated, Literal
from pydantic import Field
from mcp.server.fastmcp import FastMCP

# === Server Initialization ===
mcp = FastMCP(
    name="Resistor Color Code Decoder",
    instructions=(
        "A tool for electronics engineers to decode and encode resistor color bands. "
        "Supports 4-band and 5-band resistors, tolerance colors, and standard E-series values."
    ),
)

# === Color Code Data ===
# Digit values (first bands)
COLOR_DIGITS: dict[str, int] = {
    "black": 0, "brown": 1, "red": 2, "orange": 3, "yellow": 4,
    "green": 5, "blue": 6, "violet": 7, "grey": 8, "gray": 8, "white": 9,
}

# Multiplier values (ohms)
COLOR_MULTIPLIERS: dict[str, float] = {
    "black": 1,          # 10^0
    "brown": 10,         # 10^1
    "red": 100,          # 10^2
    "orange": 1_000,     # 10^3 (1k)
    "yellow": 10_000,    # 10^4 (10k)
    "green": 100_000,    # 10^5 (100k)
    "blue": 1_000_000,   # 10^6 (1M)
    "violet": 10_000_000,# 10^7 (10M)
    "grey": 0.01,        # 10^-2
    "gray": 0.01,
    "gold": 0.1,         # 10^-1
    "silver": 0.01,      # 10^-2
}

# Tolerance values (percentage)
TOLERANCE_VALUES: dict[str, float] = {
    "brown": 1.0,
    "red": 2.0,
    "green": 0.5,
    "blue": 0.25,
    "violet": 0.1,
    "grey": 0.05,
    "gray": 0.05,
    "gold": 5.0,
    "silver": 10.0,
    "none": 20.0,
}

# Reverse lookups for encoding
DIGIT_COLORS = {v: k.capitalize() for k, v in COLOR_DIGITS.items() if k != "gray"}
MULTIPLIER_COLORS = {
    1: "Black", 10: "Brown", 100: "Red", 1_000: "Orange",
    10_000: "Yellow", 100_000: "Green", 1_000_000: "Blue",
    10_000_000: "Violet", 0.1: "Gold", 0.01: "Silver",
}
TOLERANCE_COLORS = {
    1.0: "Brown", 2.0: "Red", 0.5: "Green", 0.25: "Blue",
    0.1: "Violet", 0.05: "Grey", 5.0: "Gold", 10.0: "Silver", 20.0: "None",
}

# E-series standard values (significant figures only, multiply by decade)
E12_VALUES = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
E24_VALUES = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1,
]
E96_VALUES = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
    1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
    1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
    2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
    3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
    5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
    7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76,
]


def _format_resistance(ohms: float) -> str:
    """Format resistance value with appropriate unit (Ω, kΩ, MΩ)."""
    if ohms >= 1_000_000:
        value = ohms / 1_000_000
        unit = "MΩ"
    elif ohms >= 1_000:
        value = ohms / 1_000
        unit = "kΩ"
    else:
        value = ohms
        unit = "Ω"
    
    # Clean up decimal places
    if value == int(value):
        return f"{int(value)}{unit}"
    elif value * 10 == int(value * 10):
        return f"{value:.1f}{unit}"
    else:
        return f"{value:.2f}{unit}"


def _normalize_color(color: str) -> str:
    """Normalize color name to lowercase, handle common variations."""
    return color.strip().lower().replace("-", "").replace("_", "")


def _find_best_multiplier(value: float) -> tuple[int, float]:
    """Find the best significant digits and multiplier for a value."""
    if value <= 0:
        return 0, 1
    
    # Normalize to 2-digit significant figure (10-99)
    multiplier = 1.0
    normalized = value
    
    while normalized >= 100:
        normalized /= 10
        multiplier *= 10
    while normalized < 10:
        normalized *= 10
        multiplier /= 10
    
    return int(round(normalized)), multiplier


# === Tools ===
@mcp.tool()
def decode_resistor_color_bands(
    band1: Annotated[str, Field(description="First color band (digit 1): Black, Brown, Red, Orange, Yellow, Green, Blue, Violet, Grey, White")],
    band2: Annotated[str, Field(description="Second color band (digit 2): same colors as band1")],
    band3: Annotated[str, Field(description="Third band - Multiplier for 4-band, or digit 3 for 5-band")],
    band4: Annotated[str, Field(description="Fourth band - Tolerance for 4-band (Gold=±5%, Silver=±10%), or multiplier for 5-band")] = "gold",
    band5: Annotated[str | None, Field(description="Fifth band (5-band only) - Tolerance: Brown=±1%, Red=±2%, Gold=±5%")] = None,
) -> str:
    """
    Decode resistor color bands to get resistance value and tolerance.
    
    Supports both 4-band and 5-band resistors:
    - 4-band: digit, digit, multiplier, tolerance (common resistors)
    - 5-band: digit, digit, digit, multiplier, tolerance (precision resistors)
    
    Examples:
        4-band: Brown, Black, Red, Gold → 1kΩ ±5%
        5-band: Brown, Black, Black, Brown, Brown → 1kΩ ±1%
    """
    # Normalize colors
    b1 = _normalize_color(band1)
    b2 = _normalize_color(band2)
    b3 = _normalize_color(band3)
    b4 = _normalize_color(band4)
    b5 = _normalize_color(band5) if band5 else None
    
    # Validate colors
    errors = []
    if b1 not in COLOR_DIGITS:
        errors.append(f"Band 1 '{band1}' is not a valid digit color")
    if b2 not in COLOR_DIGITS:
        errors.append(f"Band 2 '{band2}' is not a valid digit color")
    
    if b5:  # 5-band resistor
        if b3 not in COLOR_DIGITS:
            errors.append(f"Band 3 '{band3}' is not a valid digit color")
        if b4 not in COLOR_MULTIPLIERS:
            errors.append(f"Band 4 '{band4}' is not a valid multiplier color")
        if b5 not in TOLERANCE_VALUES:
            errors.append(f"Band 5 '{band5}' is not a valid tolerance color")
    else:  # 4-band resistor
        if b3 not in COLOR_MULTIPLIERS:
            errors.append(f"Band 3 '{band3}' is not a valid multiplier color")
        if b4 not in TOLERANCE_VALUES:
            errors.append(f"Band 4 '{band4}' is not a valid tolerance color")
    
    if errors:
        return "❌ Invalid color codes:\n• " + "\n• ".join(errors)
    
    # Calculate resistance
    if b5:  # 5-band
        digits = COLOR_DIGITS[b1] * 100 + COLOR_DIGITS[b2] * 10 + COLOR_DIGITS[b3]
        multiplier = COLOR_MULTIPLIERS[b4]
        tolerance = TOLERANCE_VALUES[b5]
    else:  # 4-band
        digits = COLOR_DIGITS[b1] * 10 + COLOR_DIGITS[b2]
        multiplier = COLOR_MULTIPLIERS[b3]
        tolerance = TOLERANCE_VALUES[b4]
    
    resistance = digits * multiplier
    formatted = _format_resistance(resistance)
    
    # Build result
    if b5:
        bands_str = f"{band1.title()}, {band2.title()}, {band3.title()}, {band4.title()}, {band5.title()}"
    else:
        bands_str = f"{band1.title()}, {band2.title()}, {band3.title()}, {band4.title()}"
    
    return f"""🔴 Resistor Decoded

**Color Bands:** {bands_str}
**Resistance:** {formatted} ±{tolerance}%
**Range:** {_format_resistance(resistance * (1 - tolerance/100))} to {_format_resistance(resistance * (1 + tolerance/100))}"""


@mcp.tool()
def encode_resistor_value(
    resistance_ohms: Annotated[float, Field(description="Resistance value in ohms (e.g., 4700 for 4.7kΩ)", gt=0)],
    tolerance_percent: Annotated[float, Field(description="Tolerance percentage: 1, 2, 5, or 10")] = 5.0,
    bands: Annotated[Literal[4, 5], Field(description="Number of bands: 4 (standard) or 5 (precision)")] = 4,
) -> str:
    """
    Encode a resistance value into color bands.
    
    Converts a resistance value (in ohms) to the corresponding color band sequence.
    
    Examples:
        4700Ω, 5% → Yellow, Violet, Red, Gold
        1000Ω, 1% → Brown, Black, Black, Brown, Brown (5-band)
    """
    # Validate tolerance
    if tolerance_percent not in TOLERANCE_COLORS:
        valid = ", ".join(f"{t}%" for t in sorted(TOLERANCE_COLORS.keys()))
        return f"❌ Invalid tolerance {tolerance_percent}%. Valid options: {valid}"
    
    # Get significant digits and multiplier
    significant, multiplier = _find_best_multiplier(resistance_ohms)
    
    # For 5-band, we need 3 significant digits (100-999)
    if bands == 5:
        # Normalize to get 3 significant digits
        value = resistance_ohms
        mult = 1.0
        while value >= 1000:
            value /= 10
            mult *= 10
        while value < 100:
            value *= 10
            mult /= 10
        
        significant_3digit = int(round(value))
        
        d1 = significant_3digit // 100
        d2 = (significant_3digit // 10) % 10
        d3 = significant_3digit % 10
        
        # Find closest multiplier
        best_mult = min(MULTIPLIER_COLORS.keys(), key=lambda m: abs(m - mult))
        mult_color = MULTIPLIER_COLORS[best_mult]
        tol_color = TOLERANCE_COLORS[tolerance_percent]
        
        actual_resistance = significant_3digit * best_mult
        
        result = f"""🎨 Resistor Color Code (5-band)

**Target:** {_format_resistance(resistance_ohms)} ±{tolerance_percent}%
**Encoded:** {_format_resistance(actual_resistance)} ±{tolerance_percent}%

**Color Bands:**
  Band 1 (Digit): **{DIGIT_COLORS.get(d1, 'Invalid')}** ({d1})
  Band 2 (Digit): **{DIGIT_COLORS.get(d2, 'Invalid')}** ({d2})
  Band 3 (Digit): **{DIGIT_COLORS.get(d3, 'Invalid')}** ({d3})
  Band 4 (Multiplier): **{mult_color}** (×{best_mult:g})
  Band 5 (Tolerance): **{tol_color}** (±{tolerance_percent}%)"""
    
    else:  # 4-band
        d1 = significant // 10
        d2 = significant % 10
        
        # Find closest multiplier
        best_mult = min(MULTIPLIER_COLORS.keys(), key=lambda m: abs(m - multiplier))
        mult_color = MULTIPLIER_COLORS[best_mult]
        tol_color = TOLERANCE_COLORS[tolerance_percent]
        
        actual_resistance = significant * best_mult
        
        result = f"""🎨 Resistor Color Code (4-band)

**Target:** {_format_resistance(resistance_ohms)} ±{tolerance_percent}%
**Encoded:** {_format_resistance(actual_resistance)} ±{tolerance_percent}%

**Color Bands:**
  Band 1 (Digit): **{DIGIT_COLORS.get(d1, 'Invalid')}** ({d1})
  Band 2 (Digit): **{DIGIT_COLORS.get(d2, 'Invalid')}** ({d2})
  Band 3 (Multiplier): **{mult_color}** (×{best_mult:g})
  Band 4 (Tolerance): **{tol_color}** (±{tolerance_percent}%)"""
    
    return result


@mcp.tool()
def find_standard_resistor(
    target_ohms: Annotated[float, Field(description="Target resistance value in ohms", gt=0)],
    series: Annotated[Literal["E12", "E24", "E96"], Field(description="Standard series: E12 (±10%), E24 (±5%), E96 (±1%)")] = "E24",
) -> str:
    """
    Find the nearest standard resistor value from E-series.
    
    Standard resistor series:
    - E12: 12 values per decade (±10% tolerance)
    - E24: 24 values per decade (±5% tolerance)
    - E96: 96 values per decade (±1% tolerance)
    
    Returns the closest standard value and nearby alternatives.
    """
    # Select series
    series_values = {"E12": E12_VALUES, "E24": E24_VALUES, "E96": E96_VALUES}[series]
    series_tolerance = {"E12": 10.0, "E24": 5.0, "E96": 1.0}[series]
    
    # Generate all standard values from 1Ω to 10MΩ
    standard_values: list[float] = []
    for decade in range(7):  # 10^0 to 10^6
        multiplier = 10 ** decade
        for sig in series_values:
            standard_values.append(sig * multiplier)
    
    # Find closest match
    standard_values.sort()
    closest = min(standard_values, key=lambda v: abs(v - target_ohms))
    
    # Find index for nearby values
    idx = standard_values.index(closest)
    
    # Get 2 below and 2 above (if available)
    nearby = []
    for i in range(max(0, idx - 2), min(len(standard_values), idx + 3)):
        v = standard_values[i]
        diff_pct = ((v - target_ohms) / target_ohms) * 100
        nearby.append((v, diff_pct, i == idx))
    
    # Build result
    result = f"""📊 Standard Resistor Finder ({series})

**Target:** {_format_resistance(target_ohms)}
**Best Match:** {_format_resistance(closest)} (±{series_tolerance}% tolerance)
**Difference:** {((closest - target_ohms) / target_ohms) * 100:+.2f}%

**Nearby Standard Values:**"""
    
    for val, diff, is_best in nearby:
        marker = " ← Best" if is_best else ""
        result += f"\n  • {_format_resistance(val):>8} ({diff:+.2f}%){marker}"
    
    # Add color code for the best match
    sig, mult = _find_best_multiplier(closest)
    d1 = sig // 10
    d2 = sig % 10
    best_mult = min(MULTIPLIER_COLORS.keys(), key=lambda m: abs(m - mult))
    
    result += f"""

**Color Code for {_format_resistance(closest)}:**
  {DIGIT_COLORS.get(d1, 'Invalid')}, {DIGIT_COLORS.get(d2, 'Invalid')}, {MULTIPLIER_COLORS[best_mult]}, {TOLERANCE_COLORS[series_tolerance]}"""
    
    return result


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
