# Electronics MCP Servers

<!-- mcp-name: io.github.wedsamuel1230/electronic-mcp-server -->

A comprehensive Model Context Protocol (MCP) server providing 14 electronics engineering tools across 3 domains.

[![PyPI version](https://badge.fury.io/py/electronics-mcp-servers.svg)](https://pypi.org/project/electronics-mcp-servers/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Installation

```bash
pip install electronics-mcp-servers
```

## Features

### 🎨 Resistor Decoder (3 tools)
- **decode_resistor_color_bands**: Convert color bands to resistance value
- **encode_resistor_value**: Convert resistance to color bands  
- **find_standard_resistor**: Find nearest E12/E24/E96 series value

### ⚡ Capacitor Calculator (4 tools)
- **calculate_capacitive_reactance**: Frequency-dependent impedance
- **calculate_rc_time_constant**: RC circuit time calculations
- **calculate_resonant_frequency**: LC tank resonance
- **suggest_capacitor_for_filter**: Filter design recommendations

### 📌 GPIO Pin Reference (7 tools)
- **get_pin_info**: Detailed pin specifications (ESP32/Arduino/STM32)
- **find_pwm_pins**: PWM-capable pin discovery
- **find_adc_pins**: ADC channel mapping
- **find_i2c_pins**: I2C bus pins
- **find_spi_pins**: SPI bus pins
- **check_pin_conflict**: Multi-pin conflict detection
- **generate_pin_diagram_ascii**: Visual pinout diagrams

## Supported Boards

- **ESP32 DevKitC**
- **Arduino UNO R3**
- **STM32F103C8T6** (Blue Pill)

## Usage

### As an MCP Server

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "electronics": {
      "command": "python",
      "args": ["-m", "servers"]
    }
  }
}
```

Or with uvx:

```json
{
  "mcpServers": {
    "electronics": {
      "command": "uvx",
      "args": ["electronics-mcp-servers"]
    }
  }
}
```

### Direct Python Usage

```python
from servers.resistor_decoder import decode_color_bands
from servers.capacitor_calculator import calculate_rc_time_constant
from servers.gpio_reference import get_pin_info

# Decode a resistor
result = decode_color_bands(["brown", "black", "red", "gold"])
# Returns: {"resistance": 1000, "tolerance": 5, "formatted": "1kΩ ±5%"}

# Calculate RC time constant
tau = calculate_rc_time_constant(10000, 100e-6)
# Returns: {"tau": 1.0, "time_63pct": 1.0, "time_full": 5.0}

# Get ESP32 pin info
pin = get_pin_info("ESP32", 32)
# Returns detailed pin capabilities
```

## Requirements

- Python 3.10+
- FastMCP (`mcp[cli]>=1.1.0`)

## License

MIT License - Copyright (c) 2026 Samuel F.

## Links

- [GitHub Repository](https://github.com/wedsamuel1230/electronic-mcp-server)
- [PyPI Package](https://pypi.org/project/electronics-mcp-servers/)
- [MCP Registry](https://registry.modelcontextprotocol.io/servers/io.github.wedsamuel1230/electronic-mcp-server)
