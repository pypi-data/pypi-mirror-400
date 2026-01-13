#!/usr/bin/env python3
"""
Combined Electronics MCP Server
Combines resistor_decoder, capacitor_calculator, and gpio_reference into a single server.
"""
from mcp.server.fastmcp import FastMCP

# Import the actual tool functions directly
import servers.resistor_decoder as resistor_module
import servers.capacitor_calculator as capacitor_module
import servers.gpio_reference as gpio_module

# Create combined server
mcp = FastMCP(
    name="electronics-mcp-server",
    instructions="""Electronics Engineering MCP Server
    
Provides 14 tools across 3 domains:

🎨 Resistor Decoder (3 tools):
- decode_resistor_color_bands: Convert color bands to resistance value
- encode_resistor_value: Convert resistance to color bands
- find_standard_resistor: Find nearest E12/E24/E96 series value

⚡ Capacitor Calculator (4 tools):
- calculate_capacitive_reactance: Frequency-dependent impedance
- calculate_rc_time_constant: RC circuit time calculations
- calculate_resonant_frequency: LC tank resonance
- suggest_capacitor_for_filter: Filter design recommendations

📌 GPIO Pin Reference (7 tools):
- get_pin_info: Detailed pin specifications (ESP32/Arduino/STM32)
- find_pwm_pins: PWM-capable pin discovery
- find_adc_pins: ADC channel mapping
- find_i2c_pins: I2C bus pins
- find_spi_pins: SPI bus pins
- check_pin_conflict: Multi-pin conflict detection
- generate_pin_diagram_ascii: Visual pinout diagrams

Supported boards: ESP32 DevKitC, Arduino UNO R3, STM32F103C8T6 (Blue Pill)
""",
)

# Register resistor tools
mcp.tool()(resistor_module.decode_resistor_color_bands)
mcp.tool()(resistor_module.encode_resistor_value)
mcp.tool()(resistor_module.find_standard_resistor)

# Register capacitor tools
mcp.tool()(capacitor_module.calculate_capacitive_reactance)
mcp.tool()(capacitor_module.calculate_rc_time_constant)
mcp.tool()(capacitor_module.calculate_resonant_frequency)
mcp.tool()(capacitor_module.suggest_capacitor_for_filter)

# Register GPIO tools
mcp.tool()(gpio_module.get_pin_info)
mcp.tool()(gpio_module.find_pwm_pins)
mcp.tool()(gpio_module.find_adc_pins)
mcp.tool()(gpio_module.find_i2c_pins)
mcp.tool()(gpio_module.find_spi_pins)
mcp.tool()(gpio_module.check_pin_conflict)
mcp.tool()(gpio_module.generate_pin_diagram_ascii)

# Run the combined server
if __name__ == "__main__":
    mcp.run()
