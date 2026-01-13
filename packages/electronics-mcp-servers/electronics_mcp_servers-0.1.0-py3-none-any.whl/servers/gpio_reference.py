"""
GPIO Pin Reference MCP Server
Provides comprehensive pin information for ESP32, Arduino UNO, and STM32 boards.

Based on official datasheets:
- ESP32: ESP32 Technical Reference Manual v4.8
- Arduino UNO: ATmega328P datasheet
- STM32: STM32F103C8T6 (Blue Pill) reference manual
"""
from mcp.server.fastmcp import FastMCP
from typing import Annotated, Literal
from pydantic import Field

# Initialize MCP server
mcp = FastMCP(
    name="gpio-reference",
    instructions="Provides GPIO pin information, pinout diagrams, and conflict detection for ESP32, Arduino UNO, and STM32 boards."
)

# ============================================================================
# PIN DATABASE - Based on Official Datasheets
# ============================================================================

PIN_DATABASE = {
    "ESP32": {
        0: {
            "name": "GPIO0",
            "functions": ["ADC2_CH1", "TOUCH1", "RTC_GPIO11", "CLK_OUT1", "EMAC_TX_CLK"],
            "notes": "Bootstrap pin - must be HIGH during boot. Connected to BOOT button on most dev boards.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": True,
            "strapping": True
        },
        1: {
            "name": "GPIO1",
            "functions": ["U0TXD", "CLK_OUT3", "EMAC_RXD2"],
            "notes": "UART0 TX - Serial debug output. Avoid using for GPIO during development.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False
        },
        2: {
            "name": "GPIO2",
            "functions": ["ADC2_CH2", "TOUCH2", "RTC_GPIO12", "HSPIWP", "SD_DATA0"],
            "notes": "Bootstrap pin - must be LOW during boot. Connected to onboard LED on many boards.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": True,
            "strapping": True
        },
        3: {
            "name": "GPIO3",
            "functions": ["U0RXD", "CLK_OUT2"],
            "notes": "UART0 RX - Serial debug input. Avoid using for GPIO during development.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False
        },
        4: {
            "name": "GPIO4",
            "functions": ["ADC2_CH0", "TOUCH0", "RTC_GPIO10", "HSPIHD", "SD_DATA1", "EMAC_TX_ER"],
            "notes": "Safe to use for most applications.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": True
        },
        5: {
            "name": "GPIO5",
            "functions": ["VSPICS0", "EMAC_RX_CLK"],
            "notes": "Bootstrap pin - strapping pin. Safe to use after boot.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False,
            "strapping": True,
            "spi": "SS"
        },
        12: {
            "name": "GPIO12",
            "functions": ["ADC2_CH5", "TOUCH5", "RTC_GPIO15", "MTDI", "HSPIQ", "SD_DATA2", "EMAC_TXD3"],
            "notes": "Bootstrap pin - sets flash voltage. Must be LOW during boot for 3.3V flash.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": True,
            "strapping": True
        },
        13: {
            "name": "GPIO13",
            "functions": ["ADC2_CH4", "TOUCH4", "RTC_GPIO14", "MTCK", "HSPID", "SD_DATA3", "EMAC_RX_ER"],
            "notes": "Safe to use for most applications.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": True
        },
        14: {
            "name": "GPIO14",
            "functions": ["ADC2_CH6", "TOUCH6", "RTC_GPIO16", "MTMS", "HSPICLK", "SD_CLK", "EMAC_TXD2"],
            "notes": "Safe to use for most applications.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": True
        },
        15: {
            "name": "GPIO15",
            "functions": ["ADC2_CH3", "TOUCH3", "RTC_GPIO13", "MTDO", "HSPICS0", "SD_CMD", "EMAC_RXD3"],
            "notes": "Bootstrap pin - must be HIGH during boot for normal operation.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": True,
            "strapping": True
        },
        18: {
            "name": "GPIO18",
            "functions": ["VSPICLK"],
            "notes": "SPI clock. Safe to use.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False,
            "spi": "SCK"
        },
        19: {
            "name": "GPIO19",
            "functions": ["VSPIQ", "U0CTS", "EMAC_TXD0"],
            "notes": "SPI MISO. Safe to use.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False,
            "spi": "MISO"
        },
        21: {
            "name": "GPIO21",
            "functions": ["VSPIHD", "EMAC_TX_EN"],
            "notes": "I2C SDA by default in Arduino. Safe to use.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False,
            "i2c": "SDA"
        },
        22: {
            "name": "GPIO22",
            "functions": ["VSPIWP", "U0RTS", "EMAC_TXD1"],
            "notes": "I2C SCL by default in Arduino. Safe to use.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False,
            "i2c": "SCL"
        },
        23: {
            "name": "GPIO23",
            "functions": ["VSPID"],
            "notes": "SPI MOSI. Safe to use.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False,
            "spi": "MOSI"
        },
        25: {
            "name": "GPIO25",
            "functions": ["ADC2_CH8", "DAC_1", "RTC_GPIO6", "EMAC_RXD0"],
            "notes": "ADC2 and DAC1 output. Safe to use.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": True,
            "dac": True
        },
        26: {
            "name": "GPIO26",
            "functions": ["ADC2_CH9", "DAC_2", "RTC_GPIO7", "EMAC_RXD1"],
            "notes": "ADC2 and DAC2 output. Safe to use.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": True,
            "dac": True
        },
        27: {
            "name": "GPIO27",
            "functions": ["ADC2_CH7", "TOUCH7", "RTC_GPIO17", "EMAC_RX_DV"],
            "notes": "Safe to use for most applications.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": True
        },
        32: {
            "name": "GPIO32",
            "functions": ["ADC1_CH4", "TOUCH9", "RTC_GPIO9", "XTAL_32K_P"],
            "notes": "ADC1 - works with WiFi. Safe to use.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": True
        },
        33: {
            "name": "GPIO33",
            "functions": ["ADC1_CH5", "TOUCH8", "RTC_GPIO8", "XTAL_32K_N"],
            "notes": "ADC1 - works with WiFi. Safe to use.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": True
        },
        34: {
            "name": "GPIO34",
            "functions": ["ADC1_CH6", "RTC_GPIO4"],
            "notes": "Input only - no internal pull-up/down. ADC1 - works with WiFi.",
            "input": True,
            "output": False,
            "pwm": False,
            "adc": True
        },
        35: {
            "name": "GPIO35",
            "functions": ["ADC1_CH7", "RTC_GPIO5"],
            "notes": "Input only - no internal pull-up/down. ADC1 - works with WiFi.",
            "input": True,
            "output": False,
            "pwm": False,
            "adc": True
        },
        36: {
            "name": "GPIO36",
            "functions": ["ADC1_CH0", "RTC_GPIO0", "SENSOR_VP"],
            "notes": "Input only - no internal pull-up/down. ADC1 - works with WiFi.",
            "input": True,
            "output": False,
            "pwm": False,
            "adc": True
        },
        39: {
            "name": "GPIO39",
            "functions": ["ADC1_CH3", "RTC_GPIO3", "SENSOR_VN"],
            "notes": "Input only - no internal pull-up/down. ADC1 - works with WiFi.",
            "input": True,
            "output": False,
            "pwm": False,
            "adc": True
        }
    },
    
    "Arduino UNO": {
        0: {
            "name": "D0",
            "functions": ["RXD", "PCINT16"],
            "notes": "UART RX - Serial communication. Avoid using for GPIO when using Serial.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": False,
            "uart": "RX"
        },
        1: {
            "name": "D1",
            "functions": ["TXD", "PCINT17"],
            "notes": "UART TX - Serial communication. Avoid using for GPIO when using Serial.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": False,
            "uart": "TX"
        },
        2: {
            "name": "D2",
            "functions": ["INT0", "PCINT18"],
            "notes": "External interrupt 0. Safe to use.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": False,
            "interrupt": True
        },
        3: {
            "name": "D3",
            "functions": ["INT1", "OC2B", "PCINT19"],
            "notes": "PWM via Timer2. External interrupt 1.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False,
            "interrupt": True
        },
        4: {
            "name": "D4",
            "functions": ["T0", "XCK", "PCINT20"],
            "notes": "Safe to use for general GPIO.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": False
        },
        5: {
            "name": "D5",
            "functions": ["OC0B", "T1", "PCINT21"],
            "notes": "PWM via Timer0.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False
        },
        6: {
            "name": "D6",
            "functions": ["OC0A", "AIN0", "PCINT22"],
            "notes": "PWM via Timer0.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False
        },
        7: {
            "name": "D7",
            "functions": ["AIN1", "PCINT23"],
            "notes": "Safe to use for general GPIO.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": False
        },
        8: {
            "name": "D8",
            "functions": ["ICP1", "CLK0", "PCINT0"],
            "notes": "Safe to use for general GPIO.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": False
        },
        9: {
            "name": "D9",
            "functions": ["OC1A", "PCINT1"],
            "notes": "PWM via Timer1 (16-bit).",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False
        },
        10: {
            "name": "D10",
            "functions": ["OC1B", "SS", "PCINT2"],
            "notes": "PWM via Timer1. SPI Slave Select.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False,
            "spi": "SS"
        },
        11: {
            "name": "D11",
            "functions": ["OC2A", "MOSI", "PCINT3"],
            "notes": "PWM via Timer2. SPI MOSI.",
            "input": True,
            "output": True,
            "pwm": True,
            "adc": False,
            "spi": "MOSI"
        },
        12: {
            "name": "D12",
            "functions": ["MISO", "PCINT4"],
            "notes": "SPI MISO. Safe to use if not using SPI.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": False,
            "spi": "MISO"
        },
        13: {
            "name": "D13",
            "functions": ["SCK", "PCINT5"],
            "notes": "SPI Clock. Connected to onboard LED.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": False,
            "spi": "SCK"
        },
        14: {
            "name": "A0",
            "functions": ["ADC0", "PCINT8"],
            "notes": "Analog input channel 0. Can be used as digital GPIO.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": True,
            "analog_channel": 0
        },
        15: {
            "name": "A1",
            "functions": ["ADC1", "PCINT9"],
            "notes": "Analog input channel 1. Can be used as digital GPIO.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": True,
            "analog_channel": 1
        },
        16: {
            "name": "A2",
            "functions": ["ADC2", "PCINT10"],
            "notes": "Analog input channel 2. Can be used as digital GPIO.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": True,
            "analog_channel": 2
        },
        17: {
            "name": "A3",
            "functions": ["ADC3", "PCINT11"],
            "notes": "Analog input channel 3. Can be used as digital GPIO.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": True,
            "analog_channel": 3
        },
        18: {
            "name": "A4",
            "functions": ["ADC4", "SDA", "PCINT12"],
            "notes": "I2C SDA. Analog input channel 4.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": True,
            "analog_channel": 4,
            "i2c": "SDA"
        },
        19: {
            "name": "A5",
            "functions": ["ADC5", "SCL", "PCINT13"],
            "notes": "I2C SCL. Analog input channel 5.",
            "input": True,
            "output": True,
            "pwm": False,
            "adc": True,
            "analog_channel": 5,
            "i2c": "SCL"
        }
    },
    
    "STM32": {
        # Port A
        0: {"name": "PA0", "functions": ["ADC1_IN0", "TIM2_CH1", "USART2_CTS", "WKUP"], "input": True, "output": True, "pwm": True, "adc": True, "notes": "ADC channel 0. Timer 2 PWM."},
        1: {"name": "PA1", "functions": ["ADC1_IN1", "TIM2_CH2", "USART2_RTS"], "input": True, "output": True, "pwm": True, "adc": True, "notes": "ADC channel 1. Timer 2 PWM."},
        2: {"name": "PA2", "functions": ["ADC1_IN2", "TIM2_CH3", "USART2_TX"], "input": True, "output": True, "pwm": True, "adc": True, "uart": "TX", "notes": "USART2 TX. ADC channel 2."},
        3: {"name": "PA3", "functions": ["ADC1_IN3", "TIM2_CH4", "USART2_RX"], "input": True, "output": True, "pwm": True, "adc": True, "uart": "RX", "notes": "USART2 RX. ADC channel 3."},
        4: {"name": "PA4", "functions": ["ADC1_IN4", "SPI1_NSS", "DAC_OUT1"], "input": True, "output": True, "pwm": False, "adc": True, "dac": True, "spi": "NSS", "notes": "SPI1 NSS. DAC output 1."},
        5: {"name": "PA5", "functions": ["ADC1_IN5", "SPI1_SCK", "DAC_OUT2"], "input": True, "output": True, "pwm": False, "adc": True, "dac": True, "spi": "SCK", "notes": "SPI1 SCK. DAC output 2. Onboard LED."},
        6: {"name": "PA6", "functions": ["ADC1_IN6", "SPI1_MISO", "TIM3_CH1"], "input": True, "output": True, "pwm": True, "adc": True, "spi": "MISO", "notes": "SPI1 MISO. Timer 3 PWM."},
        7: {"name": "PA7", "functions": ["ADC1_IN7", "SPI1_MOSI", "TIM3_CH2"], "input": True, "output": True, "pwm": True, "adc": True, "spi": "MOSI", "notes": "SPI1 MOSI. Timer 3 PWM."},
        8: {"name": "PA8", "functions": ["TIM1_CH1", "USART1_CK", "MCO"], "input": True, "output": True, "pwm": True, "adc": False, "notes": "Timer 1 PWM. Master clock output."},
        9: {"name": "PA9", "functions": ["TIM1_CH2", "USART1_TX"], "input": True, "output": True, "pwm": True, "adc": False, "uart": "TX", "notes": "USART1 TX. Timer 1 PWM."},
        10: {"name": "PA10", "functions": ["TIM1_CH3", "USART1_RX"], "input": True, "output": True, "pwm": True, "adc": False, "uart": "RX", "notes": "USART1 RX. Timer 1 PWM."},
        11: {"name": "PA11", "functions": ["TIM1_CH4", "USART1_CTS", "USB_DM"], "input": True, "output": True, "pwm": True, "adc": False, "notes": "USB D-. Timer 1 PWM."},
        12: {"name": "PA12", "functions": ["TIM1_ETR", "USART1_RTS", "USB_DP"], "input": True, "output": True, "pwm": False, "adc": False, "notes": "USB D+. External trigger."},
        13: {"name": "PA13", "functions": ["JTMS", "SWDIO"], "input": True, "output": True, "pwm": False, "adc": False, "notes": "SWD programming data. Keep free for debugging."},
        14: {"name": "PA14", "functions": ["JTCK", "SWCLK"], "input": True, "output": True, "pwm": False, "adc": False, "notes": "SWD programming clock. Keep free for debugging."},
        15: {"name": "PA15", "functions": ["JTDI", "TIM2_CH1", "SPI1_NSS"], "input": True, "output": True, "pwm": True, "adc": False, "notes": "SPI1 NSS alternate. Timer 2 PWM."},
        
        # Port B
        16: {"name": "PB0", "functions": ["ADC1_IN8", "TIM3_CH3"], "input": True, "output": True, "pwm": True, "adc": True, "notes": "ADC channel 8. Timer 3 PWM."},
        17: {"name": "PB1", "functions": ["ADC1_IN9", "TIM3_CH4"], "input": True, "output": True, "pwm": True, "adc": True, "notes": "ADC channel 9. Timer 3 PWM."},
        18: {"name": "PB2", "functions": ["BOOT1"], "input": True, "output": True, "pwm": False, "adc": False, "notes": "Boot mode selection pin."},
        19: {"name": "PB3", "functions": ["JTDO", "TIM2_CH2", "SPI1_SCK"], "input": True, "output": True, "pwm": True, "adc": False, "notes": "SPI1 SCK alternate. Timer 2 PWM."},
        20: {"name": "PB4", "functions": ["JNTRST", "TIM3_CH1", "SPI1_MISO"], "input": True, "output": True, "pwm": True, "adc": False, "notes": "SPI1 MISO alternate. Timer 3 PWM."},
        21: {"name": "PB5", "functions": ["TIM3_CH2", "SPI1_MOSI", "I2C1_SMBA"], "input": True, "output": True, "pwm": True, "adc": False, "notes": "SPI1 MOSI alternate. Timer 3 PWM."},
        22: {"name": "PB6", "functions": ["TIM4_CH1", "I2C1_SCL", "USART1_TX"], "input": True, "output": True, "pwm": True, "adc": False, "i2c": "SCL", "notes": "I2C1 SCL. Timer 4 PWM."},
        23: {"name": "PB7", "functions": ["TIM4_CH2", "I2C1_SDA", "USART1_RX"], "input": True, "output": True, "pwm": True, "adc": False, "i2c": "SDA", "notes": "I2C1 SDA. Timer 4 PWM."},
        24: {"name": "PB8", "functions": ["TIM4_CH3", "I2C1_SCL"], "input": True, "output": True, "pwm": True, "adc": False, "i2c": "SCL", "notes": "I2C1 SCL alternate. Timer 4 PWM."},
        25: {"name": "PB9", "functions": ["TIM4_CH4", "I2C1_SDA"], "input": True, "output": True, "pwm": True, "adc": False, "i2c": "SDA", "notes": "I2C1 SDA alternate. Timer 4 PWM."},
        26: {"name": "PB10", "functions": ["TIM2_CH3", "I2C2_SCL", "USART3_TX"], "input": True, "output": True, "pwm": True, "adc": False, "i2c": "SCL", "notes": "I2C2 SCL. Timer 2 PWM."},
        27: {"name": "PB11", "functions": ["TIM2_CH4", "I2C2_SDA", "USART3_RX"], "input": True, "output": True, "pwm": True, "adc": False, "i2c": "SDA", "notes": "I2C2 SDA. Timer 2 PWM."},
        28: {"name": "PB12", "functions": ["SPI2_NSS", "I2C2_SMBA", "TIM1_BKIN"], "input": True, "output": True, "pwm": False, "adc": False, "spi": "NSS", "notes": "SPI2 NSS. I2C2 SMBA."},
        29: {"name": "PB13", "functions": ["SPI2_SCK", "TIM1_CH1N", "USART3_CTS"], "input": True, "output": True, "pwm": True, "adc": False, "spi": "SCK", "notes": "SPI2 SCK. Timer 1 complementary."},
        30: {"name": "PB14", "functions": ["SPI2_MISO", "TIM1_CH2N", "USART3_RTS"], "input": True, "output": True, "pwm": True, "adc": False, "spi": "MISO", "notes": "SPI2 MISO. Timer 1 complementary."},
        31: {"name": "PB15", "functions": ["SPI2_MOSI", "TIM1_CH3N"], "input": True, "output": True, "pwm": True, "adc": False, "spi": "MOSI", "notes": "SPI2 MOSI. Timer 1 complementary."},
        
        # Port C (limited pins on Blue Pill)
        32: {"name": "PC13", "functions": ["TAMPER-RTC"], "input": True, "output": True, "pwm": False, "adc": False, "notes": "Onboard LED on Blue Pill. RTC tamper detection."},
        33: {"name": "PC14", "functions": ["OSC32_IN"], "input": True, "output": True, "pwm": False, "adc": False, "notes": "32.768 kHz crystal oscillator input."},
        34: {"name": "PC15", "functions": ["OSC32_OUT"], "input": True, "output": True, "pwm": False, "adc": False, "notes": "32.768 kHz crystal oscillator output."}
    }
}


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

@mcp.tool()
def get_pin_info(
    board_type: Annotated[
        Literal["ESP32", "Arduino UNO", "STM32"], 
        Field(description="Type of development board")
    ],
    pin_number: Annotated[int, Field(description="Pin number to query", ge=0)]
) -> str:
    """
    Get detailed information about a specific GPIO pin.
    
    Returns pin name, alternative functions, capabilities (PWM, ADC, etc.),
    and important notes about usage restrictions or recommendations.
    
    Args:
        board_type: Development board type (ESP32, Arduino UNO, or STM32)
        pin_number: Physical pin number
        
    Returns:
        Formatted pin information including functions and notes
    """
    if board_type not in PIN_DATABASE:
        return f"❌ Unsupported board type: {board_type}\nSupported: ESP32, Arduino UNO, STM32"
    
    board_pins = PIN_DATABASE[board_type]
    if pin_number not in board_pins:
        available = sorted(board_pins.keys())
        return f"❌ Pin {pin_number} not found on {board_type}\nAvailable pins: {', '.join(map(str, available[:10]))}{'...' if len(available) > 10 else ''}"
    
    pin = board_pins[pin_number]
    
    # Build capabilities list
    capabilities = []
    if pin.get("input"): capabilities.append("Input")
    if pin.get("output"): capabilities.append("Output")
    if pin.get("pwm"): capabilities.append("PWM")
    if pin.get("adc"): capabilities.append("ADC")
    if pin.get("dac"): capabilities.append("DAC")
    if pin.get("interrupt"): capabilities.append("Interrupt")
    
    # Build peripheral info
    peripherals = []
    if pin.get("uart"): peripherals.append(f"UART {pin['uart']}")
    if pin.get("spi"): peripherals.append(f"SPI {pin['spi']}")
    if pin.get("i2c"): peripherals.append(f"I2C {pin['i2c']}")
    if pin.get("analog_channel") is not None: peripherals.append(f"ADC Channel {pin['analog_channel']}")
    
    result = f"📌 {board_type} Pin {pin_number}\n\n"
    result += f"**Name:** {pin['name']}\n\n"
    result += f"**Capabilities:** {', '.join(capabilities)}\n\n"
    result += f"**Alternative Functions:**\n"
    for func in pin['functions']:
        result += f"  • {func}\n"
    
    if peripherals:
        result += f"\n**Peripherals:** {', '.join(peripherals)}\n"
    
    if pin.get("notes"):
        result += f"\n⚠️ **Notes:** {pin['notes']}\n"
    
    return result


@mcp.tool()
def find_pwm_pins(
    board_type: Annotated[
        Literal["ESP32", "Arduino UNO", "STM32"], 
        Field(description="Type of development board")
    ]
) -> str:
    """
    List all pins that support PWM (Pulse Width Modulation) output.
    
    PWM pins are essential for:
    - LED dimming
    - Motor speed control
    - Servo control
    - Analog-like output generation
    
    Args:
        board_type: Development board type
        
    Returns:
        List of PWM-capable pins with timer information
    """
    if board_type not in PIN_DATABASE:
        return f"❌ Unsupported board type: {board_type}"
    
    board_pins = PIN_DATABASE[board_type]
    pwm_pins = []
    
    for pin_num, pin_info in board_pins.items():
        if pin_info.get("pwm", False):
            # Extract timer info from functions
            timer_info = [f for f in pin_info.get("functions", []) if "TIM" in f or "OC" in f or "PWM" in f]
            timer_str = f" ({timer_info[0]})" if timer_info else ""
            pwm_pins.append((pin_num, pin_info['name'], timer_str))
    
    if not pwm_pins:
        return f"❌ No PWM pins found for {board_type}"
    
    result = f"⚡ PWM-Capable Pins for {board_type}\n\n"
    result += f"Found **{len(pwm_pins)} pins** with PWM support:\n\n"
    
    for pin_num, name, timer in sorted(pwm_pins):
        result += f"  • Pin {pin_num:2d} ({name:8s}){timer}\n"
    
    result += f"\n💡 **Tip:** PWM frequency and resolution depend on the timer configuration."
    
    return result


@mcp.tool()
def find_adc_pins(
    board_type: Annotated[
        Literal["ESP32", "Arduino UNO", "STM32"], 
        Field(description="Type of development board")
    ]
) -> str:
    """
    List all pins that support ADC (Analog-to-Digital Conversion) input.
    
    ADC pins are used for reading:
    - Sensors (temperature, light, pressure)
    - Potentiometers and analog controls
    - Battery voltage monitoring
    - Analog signals
    
    Args:
        board_type: Development board type
        
    Returns:
        List of ADC-capable pins with channel information and notes
    """
    if board_type not in PIN_DATABASE:
        return f"❌ Unsupported board type: {board_type}"
    
    board_pins = PIN_DATABASE[board_type]
    adc_pins = []
    
    for pin_num, pin_info in board_pins.items():
        if pin_info.get("adc", False):
            # Extract ADC channel info
            adc_info = [f for f in pin_info.get("functions", []) if "ADC" in f]
            adc_str = f" - {adc_info[0]}" if adc_info else ""
            
            # Check for special notes
            notes = ""
            if "Input only" in pin_info.get("notes", ""):
                notes = " [INPUT ONLY]"
            elif "ADC1" in adc_str and board_type == "ESP32":
                notes = " [WiFi Compatible]"
            elif "ADC2" in adc_str and board_type == "ESP32":
                notes = " [Not usable with WiFi]"
            
            adc_pins.append((pin_num, pin_info['name'], adc_str, notes))
    
    if not adc_pins:
        return f"❌ No ADC pins found for {board_type}"
    
    result = f"📊 ADC-Capable Pins for {board_type}\n\n"
    result += f"Found **{len(adc_pins)} pins** with ADC support:\n\n"
    
    for pin_num, name, adc_ch, notes in sorted(adc_pins):
        result += f"  • Pin {pin_num:2d} ({name:8s}){adc_ch}{notes}\n"
    
    if board_type == "ESP32":
        result += f"\n⚠️ **ESP32 Important Notes:**"
        result += f"\n  • ADC1 channels work with WiFi enabled"
        result += f"\n  • ADC2 channels cannot be used when WiFi is active"
        result += f"\n  • GPIO 34-39 are input-only (no pull-up/down resistors)"
    elif board_type == "Arduino UNO":
        result += f"\n💡 **Tip:** Analog pins can also be used as digital GPIO (D14-D19)"
    
    return result


@mcp.tool()
def find_i2c_pins(
    board_type: Annotated[
        Literal["ESP32", "Arduino UNO", "STM32"], 
        Field(description="Type of development board")
    ]
) -> str:
    """
    List all pins that support I2C (Inter-Integrated Circuit) communication.
    
    I2C is used for:
    - Sensor modules (IMU, temperature, pressure)
    - OLED/LCD displays
    - EEPROM chips
    - RTC modules
    
    Args:
        board_type: Development board type
        
    Returns:
        I2C pin pairs (SDA/SCL) with notes
    """
    if board_type not in PIN_DATABASE:
        return f"❌ Unsupported board type: {board_type}"
    
    board_pins = PIN_DATABASE[board_type]
    i2c_pins = {"SDA": [], "SCL": []}
    
    for pin_num, pin_info in board_pins.items():
        if pin_info.get("i2c"):
            role = pin_info["i2c"]
            i2c_pins[role].append((pin_num, pin_info['name']))
    
    if not i2c_pins["SDA"] and not i2c_pins["SCL"]:
        return f"❌ No I2C pins found for {board_type}"
    
    result = f"🔗 I2C-Capable Pins for {board_type}\n\n"
    
    if i2c_pins["SDA"]:
        result += "**SDA (Data) Pins:**\n"
        for pin_num, name in sorted(i2c_pins["SDA"]):
            result += f"  • Pin {pin_num:2d} ({name})\n"
        result += "\n"
    
    if i2c_pins["SCL"]:
        result += "**SCL (Clock) Pins:**\n"
        for pin_num, name in sorted(i2c_pins["SCL"]):
            result += f"  • Pin {pin_num:2d} ({name})\n"
    
    result += f"\n💡 **Default I2C Configuration:**\n"
    if board_type == "ESP32":
        result += "  • SDA: GPIO21, SCL: GPIO22 (configurable)"
    elif board_type == "Arduino UNO":
        result += "  • SDA: A4 (Pin 18), SCL: A5 (Pin 19)"
    elif board_type == "STM32":
        result += "  • I2C1: SDA: PB7, SCL: PB6"
        result += "\n  • I2C2: SDA: PB11, SCL: PB10"
    
    return result


@mcp.tool()
def find_spi_pins(
    board_type: Annotated[
        Literal["ESP32", "Arduino UNO", "STM32"], 
        Field(description="Type of development board")
    ]
) -> str:
    """
    List all pins that support SPI (Serial Peripheral Interface) communication.
    
    SPI is used for:
    - SD cards
    - Display modules (TFT, ePaper)
    - Flash memory chips
    - High-speed sensor communication
    
    Args:
        board_type: Development board type
        
    Returns:
        SPI pin assignments (MOSI, MISO, SCK, SS/NSS)
    """
    if board_type not in PIN_DATABASE:
        return f"❌ Unsupported board type: {board_type}"
    
    board_pins = PIN_DATABASE[board_type]
    spi_pins = {"MOSI": [], "MISO": [], "SCK": [], "SS": [], "NSS": []}
    
    for pin_num, pin_info in board_pins.items():
        if pin_info.get("spi"):
            role = pin_info["spi"]
            if role in spi_pins:
                spi_pins[role].append((pin_num, pin_info['name']))
    
    has_spi = any(spi_pins.values())
    if not has_spi:
        return f"❌ No SPI pins found for {board_type}"
    
    result = f"⚡ SPI-Capable Pins for {board_type}\n\n"
    
    for role in ["MOSI", "MISO", "SCK", "SS", "NSS"]:
        if spi_pins[role]:
            result += f"**{role} Pins:**\n"
            for pin_num, name in sorted(spi_pins[role]):
                result += f"  • Pin {pin_num:2d} ({name})\n"
            result += "\n"
    
    result += f"💡 **Default SPI Configuration:**\n"
    if board_type == "ESP32":
        result += "  • VSPI: MOSI: 23, MISO: 19, SCK: 18, SS: 5\n"
        result += "  • HSPI: MOSI: 13, MISO: 12, SCK: 14, SS: 15"
    elif board_type == "Arduino UNO":
        result += "  • MOSI: D11, MISO: D12, SCK: D13, SS: D10"
    elif board_type == "STM32":
        result += "  • SPI1: MOSI: PA7, MISO: PA6, SCK: PA5, NSS: PA4\n"
        result += "  • SPI2: MOSI: PB15, MISO: PB14, SCK: PB13, NSS: PB12"
    
    return result


@mcp.tool()
def check_pin_conflict(
    board_type: Annotated[
        Literal["ESP32", "Arduino UNO", "STM32"], 
        Field(description="Type of development board")
    ],
    pin_list: Annotated[list[int], Field(description="List of pin numbers to check for conflicts")]
) -> str:
    """
    Check if multiple pins have conflicting functions or usage restrictions.
    
    Detects conflicts such as:
    - Using ADC2 pins with WiFi on ESP32
    - Using UART pins during serial debugging
    - Strapping pins that affect boot behavior
    - Shared peripheral buses (SPI, I2C)
    
    Args:
        board_type: Development board type
        pin_list: List of pin numbers you plan to use
        
    Returns:
        Conflict analysis with warnings and recommendations
    """
    if board_type not in PIN_DATABASE:
        return f"❌ Unsupported board type: {board_type}"
    
    board_pins = PIN_DATABASE[board_type]
    conflicts = []
    warnings = []
    info = []
    
    # Validate all pins exist
    invalid_pins = [p for p in pin_list if p not in board_pins]
    if invalid_pins:
        return f"❌ Invalid pins for {board_type}: {invalid_pins}"
    
    # Check for input-only pins used as outputs
    for pin_num in pin_list:
        pin = board_pins[pin_num]
        if not pin.get("output", True):
            conflicts.append(f"Pin {pin_num} ({pin['name']}) is INPUT ONLY - cannot drive outputs")
    
    # Board-specific checks
    if board_type == "ESP32":
        # Check for strapping pins
        strapping = [p for p in pin_list if board_pins[p].get("strapping", False)]
        if strapping:
            warnings.append(f"Strapping pins detected: {strapping} - These affect boot behavior")
        
        # Check for ADC2 + WiFi conflict
        adc2_pins = []
        for pin_num in pin_list:
            functions = board_pins[pin_num].get("functions", [])
            if any("ADC2" in f for f in functions):
                adc2_pins.append(pin_num)
        if adc2_pins:
            warnings.append(f"ADC2 pins {adc2_pins} cannot be used when WiFi is enabled")
        
        # Check for UART pins
        if 1 in pin_list or 3 in pin_list:
            warnings.append("GPIO1/GPIO3 are UART0 TX/RX - avoid using during serial debugging")
    
    elif board_type == "Arduino UNO":
        # Check for UART pins
        if 0 in pin_list or 1 in pin_list:
            warnings.append("D0/D1 are UART TX/RX - avoid using when Serial communication is active")
        
        # Check for SPI conflict
        spi_pins = [p for p in pin_list if p in [10, 11, 12, 13]]
        if spi_pins and len(spi_pins) < 4:
            info.append(f"Partial SPI pins used: {spi_pins} - Ensure SPI library doesn't interfere")
    
    elif board_type == "STM32":
        # Check for SWD pins (PA13, PA14)
        if 13 in pin_list or 14 in pin_list:
            conflicts.append("PA13/PA14 are SWD programming pins - using them disables debugging!")
        
        # Check for USB pins
        if 11 in pin_list or 12 in pin_list:
            warnings.append("PA11/PA12 are USB D-/D+ - avoid using if USB functionality is needed")
    
    # Check for shared peripherals
    i2c_pins = [p for p in pin_list if board_pins[p].get("i2c")]
    if len(i2c_pins) >= 2:
        info.append(f"I2C pins detected: {i2c_pins} - Both SDA and SCL must be available for I2C bus")
    
    spi_pins = [p for p in pin_list if board_pins[p].get("spi")]
    if len(spi_pins) >= 3:
        info.append(f"SPI pins detected: {spi_pins} - MOSI, MISO, SCK must all be available for SPI bus")
    
    # Build result
    result = f"🔍 Pin Conflict Analysis for {board_type}\n\n"
    result += f"**Checking pins:** {', '.join(map(str, sorted(pin_list)))}\n\n"
    
    if conflicts:
        result += "❌ **CONFLICTS (Must Fix):**\n"
        for conflict in conflicts:
            result += f"  • {conflict}\n"
        result += "\n"
    
    if warnings:
        result += "⚠️ **WARNINGS (Review Carefully):**\n"
        for warning in warnings:
            result += f"  • {warning}\n"
        result += "\n"
    
    if info:
        result += "ℹ️ **INFORMATION:**\n"
        for i in info:
            result += f"  • {i}\n"
        result += "\n"
    
    if not conflicts and not warnings:
        result += "✅ **No conflicts detected!** Pin selection looks good.\n"
    
    return result


@mcp.tool()
def generate_pin_diagram_ascii(
    board_type: Annotated[
        Literal["ESP32", "Arduino UNO", "STM32"], 
        Field(description="Type of development board")
    ]
) -> str:
    """
    Generate an ASCII art pinout diagram for the development board.
    
    Shows physical pin layout with pin numbers, names, and key functions
    in an easy-to-read text format.
    
    Args:
        board_type: Development board type
        
    Returns:
        ASCII art pinout diagram
    """
    if board_type == "ESP32":
        return """
╔══════════════════════════════════════════════════════════════════════╗
║                      ESP32 DevKit v1 Pinout                          ║
╚══════════════════════════════════════════════════════════════════════╝

       Left Side                              Right Side
    ┌──────────────┐                      ┌──────────────┐
    │   EN (RESET) │                      │   GND        │
    │   VP (GPIO36)│──ADC1_CH0            │   GPIO23     │──VSPI_MOSI
    │   VN (GPIO39)│──ADC1_CH3            │   GPIO22     │──I2C_SCL
    │   GPIO34     │──ADC1_CH6 (IN)       │   GPIO1/TX0  │──UART
    │   GPIO35     │──ADC1_CH7 (IN)       │   GPIO3/RX0  │──UART
    │   GPIO32     │──ADC1_CH4            │   GPIO21     │──I2C_SDA
    │   GPIO33     │──ADC1_CH5            │   GND        │
    │   GPIO25     │──DAC1, ADC2_CH8      │   GPIO19     │──VSPI_MISO
    │   GPIO26     │──DAC2, ADC2_CH9      │   GPIO18     │──VSPI_SCK
    │   GPIO27     │──ADC2_CH7            │   GPIO5      │──VSPI_SS
    │   GPIO14     │──ADC2_CH6            │   GPIO17/TX2 │
    │   GPIO12     │──ADC2_CH5 (STRAP)    │   GPIO16/RX2 │
    │   GND        │                      │   GPIO4      │──ADC2_CH0
    │   GPIO13     │──ADC2_CH4            │   GPIO0      │──BOOT (STRAP)
    │   GPIO9/SD2  │──Flash               │   GPIO2      │──LED (STRAP)
    │   GPIO10/SD3 │──Flash               │   GPIO15     │──ADC2_CH3 (STRAP)
    │   GPIO11/CMD │──Flash               │   GND        │
    │   VIN        │                      │   3V3        │
    └──────────────┘                      └──────────────┘

⚠️  STRAPPING PINS (affect boot): GPIO0, GPIO2, GPIO5, GPIO12, GPIO15
⚠️  ADC2 pins cannot be used with WiFi active
⚠️  GPIO34-39 are INPUT ONLY (no internal pull resistors)
"""
    
    elif board_type == "Arduino UNO":
        return """
╔══════════════════════════════════════════════════════════════════════╗
║                     Arduino UNO R3 Pinout                            ║
╚══════════════════════════════════════════════════════════════════════╝

        Digital Pins                    Analog Pins & Power
    ┌──────────────────┐            ┌─────────────────────┐
    │ [ ] NC           │            │ AREF [ ]            │
    │ [ ] IOREF        │            │ GND  [ ]            │
    │ [ ] RESET        │            │ A0   [ ]──ADC0      │
    │ [ ] 3.3V         │            │ A1   [ ]──ADC1      │
    │ [ ] 5V           │            │ A2   [ ]──ADC2      │
    │ [ ] GND          │            │ A3   [ ]──ADC3      │
    │ [ ] GND          │            │ A4   [ ]──ADC4/SDA  │
    │ [ ] VIN          │            │ A5   [ ]──ADC5/SCL  │
    │                  │            └─────────────────────┘
    │ [ ] D0/RX    ──UART RX                              │
    │ [ ] D1/TX    ──UART TX                              │
    │ [ ] D2       ──INT0                                 │
    │ [~] D3       ──INT1, PWM (Timer2)                   │
    │ [ ] D4                                              │
    │ [~] D5       ──PWM (Timer0)                         │
    │ [~] D6       ──PWM (Timer0)                         │
    │ [ ] D7                                              │
    │ [ ] D8                                              │
    │ [~] D9       ──PWM (Timer1)                         │
    │ [~] D10/SS   ──PWM (Timer1), SPI SS                 │
    │ [~] D11/MOSI ──PWM (Timer2), SPI MOSI               │
    │ [ ] D12/MISO ──SPI MISO                             │
    │ [ ] D13/SCK  ──SPI SCK, Onboard LED                 │
    └──────────────────────────────────────────────────────┘

[~] = PWM capable
⚠️  D0/D1 used for Serial - avoid during debugging
⚠️  D13 connected to onboard LED
💡  Analog pins A0-A5 can be used as digital pins D14-D19
"""
    
    elif board_type == "STM32":
        return """
╔══════════════════════════════════════════════════════════════════════╗
║               STM32F103C8T6 Blue Pill Pinout                         ║
╚══════════════════════════════════════════════════════════════════════╝

       Left Side                              Right Side
    ┌──────────────┐                      ┌──────────────┐
    │   VBAT       │                      │   GND        │
    │   PC13  [LED]│                      │   GND        │
    │   PC14       │──OSC32_IN            │   3V3        │
    │   PC15       │──OSC32_OUT           │   NRST       │
    │   PA0        │──ADC1_IN0, TIM2_CH1  │   PB11       │──I2C2_SDA
    │   PA1        │──ADC1_IN1, TIM2_CH2  │   PB10       │──I2C2_SCL
    │   PA2        │──ADC1_IN2, USART2_TX │   PB1        │──ADC1_IN9
    │   PA3        │──ADC1_IN3, USART2_RX │   PB0        │──ADC1_IN8
    │   PA4        │──ADC1_IN4, DAC1, NSS │   PA7        │──SPI1_MOSI
    │   PA5  [LED] │──ADC1_IN5, DAC2, SCK │   PA6        │──SPI1_MISO
    │   PA6        │──ADC1_IN6, MISO      │   PA5        │──SPI1_SCK
    │   PA7        │──ADC1_IN7, MOSI      │   PA4        │──SPI1_NSS
    │   PB0        │──ADC1_IN8, TIM3_CH3  │   PA3        │──USART2_RX
    │   PB1        │──ADC1_IN9, TIM3_CH4  │   PA2        │──USART2_TX
    │   PB10       │──I2C2_SCL, TIM2_CH3  │   PA1        │──USART1_RTS
    │   PB11       │──I2C2_SDA, TIM2_CH4  │   PA0        │──USART1_CTS
    │   BOOT1      │                      │   PC15       │
    │   BOOT0      │                      │   PC14       │
    │   PB12       │──SPI2_NSS            │   PC13       │──LED
    │   PB13       │──SPI2_SCK            │   VBAT       │
    │   PB14       │──SPI2_MISO           │   ---        │
    │   PB15       │──SPI2_MOSI           │   ---        │
    │   PA8        │──TIM1_CH1, MCO       │   PB9        │──I2C1_SDA
    │   PA9        │──USART1_TX           │   PB8        │──I2C1_SCL
    │   PA10       │──USART1_RX           │   PB7        │──I2C1_SDA
    │   PA11       │──USB_DM, TIM1_CH4    │   PB6        │──I2C1_SCL
    │   PA12       │──USB_DP              │   PB5        │──TIM3_CH2
    │   PA13  [SWD]│──SWDIO               │   PB4        │──TIM3_CH1
    │   PA14  [SWD]│──SWCLK               │   PB3        │──TIM2_CH2
    │   PA15       │──TIM2_CH1            │   PA15       │
    │   PB3        │──TIM2_CH2, SPI1_SCK  │   PA14  [SWD]│──SWCLK
    │   PB4        │──TIM3_CH1, SPI1_MISO │   PA13  [SWD]│──SWDIO
    │   PB5        │──TIM3_CH2, SPI1_MOSI │   PA12       │──USB_DP
    │   PB6        │──I2C1_SCL, TIM4_CH1  │   PA11       │──USB_DM
    │   PB7        │──I2C1_SDA, TIM4_CH2  │   PA10       │
    │   PB8        │──I2C1_SCL, TIM4_CH3  │   PA9        │
    │   PB9        │──I2C1_SDA, TIM4_CH4  │   PA8        │
    │   5V         │                      │   PB15       │
    │   GND        │                      │   PB14       │
    │   3V3        │                      │   PB13       │
    └──────────────┘                      │   PB12       │
                                          │   GND        │
                                          │   GND        │
                                          │   3V3        │
                                          └──────────────┘

⚠️  PA13/PA14 are SWD programming pins - DO NOT USE or debugging disabled!
⚠️  PA11/PA12 are USB D-/D+ - needed for USB functionality
💡  PC13 has onboard LED (active LOW)
"""
    
    return f"❌ No diagram available for {board_type}"


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    mcp.run()
