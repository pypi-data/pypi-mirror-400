"""
Tests for GPIO Pin Reference MCP Server
Tests pin database accuracy, tool functionality, and conflict detection.
"""
import pytest
from servers.gpio_reference import (
    get_pin_info,
    find_pwm_pins,
    find_adc_pins,
    find_i2c_pins,
    find_spi_pins,
    check_pin_conflict,
    generate_pin_diagram_ascii,
    PIN_DATABASE
)


# ============================================================================
# DATABASE INTEGRITY TESTS
# ============================================================================

class TestPinDatabase:
    """Test the integrity and completeness of the pin database."""
    
    def test_all_boards_present(self):
        """Verify all required boards are in the database."""
        assert "ESP32" in PIN_DATABASE
        assert "Arduino UNO" in PIN_DATABASE
        assert "STM32" in PIN_DATABASE
    
    def test_esp32_critical_pins(self):
        """Verify ESP32 has critical pins defined."""
        esp32 = PIN_DATABASE["ESP32"]
        # Strapping pins
        assert 0 in esp32
        assert 2 in esp32
        assert 5 in esp32
        assert 12 in esp32
        assert 15 in esp32
        # I2C default pins
        assert 21 in esp32
        assert 22 in esp32
        # SPI pins
        assert 18 in esp32
        assert 19 in esp32
        assert 23 in esp32
    
    def test_arduino_uno_all_pins(self):
        """Verify Arduino UNO has all 20 pins."""
        uno = PIN_DATABASE["Arduino UNO"]
        # Digital pins 0-13
        for i in range(14):
            assert i in uno, f"Missing D{i}"
        # Analog pins 14-19 (A0-A5)
        for i in range(14, 20):
            assert i in uno, f"Missing A{i-14} (pin {i})"
    
    def test_stm32_port_coverage(self):
        """Verify STM32 has pins from all ports."""
        stm32 = PIN_DATABASE["STM32"]
        # Check Port A pins exist
        pa_pins = [k for k, v in stm32.items() if v['name'].startswith('PA')]
        assert len(pa_pins) > 0, "No Port A pins"
        # Check Port B pins exist
        pb_pins = [k for k, v in stm32.items() if v['name'].startswith('PB')]
        assert len(pb_pins) > 0, "No Port B pins"
        # Check Port C pins exist
        pc_pins = [k for k, v in stm32.items() if v['name'].startswith('PC')]
        assert len(pc_pins) > 0, "No Port C pins"
    
    def test_pin_structure_completeness(self):
        """Verify all pins have required fields."""
        for board, pins in PIN_DATABASE.items():
            for pin_num, pin_data in pins.items():
                assert "name" in pin_data, f"{board} pin {pin_num} missing name"
                assert "functions" in pin_data, f"{board} pin {pin_num} missing functions"
                assert isinstance(pin_data["functions"], list), f"{board} pin {pin_num} functions not a list"
                assert "input" in pin_data, f"{board} pin {pin_num} missing input capability"
                assert "output" in pin_data, f"{board} pin {pin_num} missing output capability"
                assert "pwm" in pin_data, f"{board} pin {pin_num} missing PWM info"
                assert "adc" in pin_data, f"{board} pin {pin_num} missing ADC info"


# ============================================================================
# GET PIN INFO TESTS
# ============================================================================

class TestGetPinInfo:
    """Test the get_pin_info tool."""
    
    def test_esp32_gpio0_boot_pin(self):
        """Test ESP32 GPIO0 (boot strapping pin)."""
        result = get_pin_info("ESP32", 0)
        assert "GPIO0" in result
        assert "Bootstrap" in result or "BOOT" in result.upper()
        assert "ADC" in result
        assert "PWM" in result
    
    def test_esp32_input_only_pins(self):
        """Test ESP32 input-only pins (34-39)."""
        for pin in [34, 35, 36, 39]:
            result = get_pin_info("ESP32", pin)
            assert "Input" in result
            assert "Input only" in result or "INPUT ONLY" in result
    
    def test_arduino_pwm_pins(self):
        """Test Arduino UNO PWM pins (3, 5, 6, 9, 10, 11)."""
        pwm_pins = [3, 5, 6, 9, 10, 11]
        for pin in pwm_pins:
            result = get_pin_info("Arduino UNO", pin)
            assert "PWM" in result
            assert "Timer" in result or "TIM" in result or "OC" in result
    
    def test_arduino_i2c_pins(self):
        """Test Arduino UNO I2C pins (A4/SDA, A5/SCL)."""
        result_sda = get_pin_info("Arduino UNO", 18)  # A4
        assert "SDA" in result_sda
        assert "I2C" in result_sda
        
        result_scl = get_pin_info("Arduino UNO", 19)  # A5
        assert "SCL" in result_scl
        assert "I2C" in result_scl
    
    def test_stm32_swd_pins(self):
        """Test STM32 SWD programming pins."""
        result_swdio = get_pin_info("STM32", 13)  # PA13
        assert "PA13" in result_swdio
        assert "SWDIO" in result_swdio or "SWD" in result_swdio
        
        result_swclk = get_pin_info("STM32", 14)  # PA14
        assert "PA14" in result_swclk
        assert "SWCLK" in result_swclk or "SWD" in result_swclk
    
    def test_invalid_board(self):
        """Test error handling for invalid board."""
        result = get_pin_info("INVALID_BOARD", 0)
        assert "❌" in result or "Unsupported" in result
    
    def test_invalid_pin_number(self):
        """Test error handling for invalid pin number."""
        result = get_pin_info("ESP32", 999)
        assert "❌" in result or "not found" in result


# ============================================================================
# FIND PWM PINS TESTS
# ============================================================================

class TestFindPwmPins:
    """Test the find_pwm_pins tool."""
    
    def test_esp32_pwm_count(self):
        """ESP32 should have many PWM-capable pins."""
        result = find_pwm_pins("ESP32")
        # ESP32 has ~25 PWM-capable pins
        assert "PWM" in result
        assert "GPIO" in result
        # Check for some known PWM pins
        for pin in ["GPIO4", "GPIO5", "GPIO13", "GPIO18"]:
            assert pin in result or f"Pin {pin[4:]}" in result
    
    def test_arduino_uno_pwm_exact(self):
        """Arduino UNO has exactly 6 PWM pins."""
        result = find_pwm_pins("Arduino UNO")
        assert "6 pins" in result
        # Check for PWM pin numbers
        for pin in ["3", "5", "6", "9", "10", "11"]:
            assert f"Pin {pin:>2}" in result or f"D{pin}" in result
    
    def test_stm32_pwm_timers(self):
        """STM32 should list pins with timer information."""
        result = find_pwm_pins("STM32")
        assert "PWM" in result
        assert "TIM" in result  # Timer info should be present
        # Check for some known PWM pins
        assert "PA0" in result or "Pin 0" in result
        assert "PB0" in result or "Pin 16" in result
    
    def test_invalid_board_pwm(self):
        """Test error handling for invalid board."""
        result = find_pwm_pins("INVALID")
        assert "❌" in result


# ============================================================================
# FIND ADC PINS TESTS
# ============================================================================

class TestFindAdcPins:
    """Test the find_adc_pins tool."""
    
    def test_esp32_adc_wifi_warning(self):
        """ESP32 should warn about ADC2 and WiFi conflict."""
        result = find_adc_pins("ESP32")
        assert "ADC" in result
        assert "ADC1" in result
        assert "ADC2" in result
        assert "WiFi" in result
    
    def test_arduino_uno_adc_count(self):
        """Arduino UNO has exactly 6 ADC channels (A0-A5)."""
        result = find_adc_pins("Arduino UNO")
        assert "6 pins" in result
        assert "A0" in result or "ADC0" in result
        assert "A5" in result or "ADC5" in result
    
    def test_stm32_adc_channels(self):
        """STM32 should list ADC channels."""
        result = find_adc_pins("STM32")
        assert "ADC" in result
        assert "PA0" in result  # Known ADC pin
        assert "ADC1_IN0" in result  # Channel info
    
    def test_esp32_input_only_note(self):
        """ESP32 ADC should note input-only pins."""
        result = find_adc_pins("ESP32")
        assert "INPUT ONLY" in result or "input-only" in result


# ============================================================================
# FIND I2C PINS TESTS
# ============================================================================

class TestFindI2cPins:
    """Test the find_i2c_pins tool."""
    
    def test_esp32_i2c_default(self):
        """Test ESP32 default I2C configuration."""
        result = find_i2c_pins("ESP32")
        assert "I2C" in result
        assert "GPIO21" in result or "Pin 21" in result  # SDA
        assert "GPIO22" in result or "Pin 22" in result  # SCL
        assert "SDA" in result
        assert "SCL" in result
    
    def test_arduino_uno_i2c(self):
        """Test Arduino UNO I2C on A4/A5."""
        result = find_i2c_pins("Arduino UNO")
        assert "A4" in result  # SDA
        assert "A5" in result  # SCL
        assert "18" in result  # Pin 18 = A4
        assert "19" in result  # Pin 19 = A5
    
    def test_stm32_i2c_multiple(self):
        """STM32 has multiple I2C buses."""
        result = find_i2c_pins("STM32")
        assert "I2C1" in result
        assert "I2C2" in result
        assert "PB6" in result or "PB7" in result


# ============================================================================
# FIND SPI PINS TESTS
# ============================================================================

class TestFindSpiPins:
    """Test the find_spi_pins tool."""
    
    def test_esp32_spi_vspi(self):
        """Test ESP32 VSPI configuration."""
        result = find_spi_pins("ESP32")
        assert "SPI" in result
        assert "VSPI" in result
        assert "MOSI" in result
        assert "MISO" in result
        assert "SCK" in result
    
    def test_arduino_uno_spi(self):
        """Test Arduino UNO SPI pins."""
        result = find_spi_pins("Arduino UNO")
        assert "D11" in result or "11" in result  # MOSI
        assert "D12" in result or "12" in result  # MISO
        assert "D13" in result or "13" in result  # SCK
        assert "D10" in result or "10" in result  # SS
    
    def test_stm32_spi_multiple(self):
        """STM32 has multiple SPI buses."""
        result = find_spi_pins("STM32")
        assert "SPI1" in result
        assert "SPI2" in result
        assert "PA5" in result or "PA7" in result  # SPI1 pins


# ============================================================================
# CHECK PIN CONFLICT TESTS
# ============================================================================

class TestCheckPinConflict:
    """Test the check_pin_conflict tool."""
    
    def test_esp32_strapping_warning(self):
        """ESP32 should warn about strapping pins."""
        result = check_pin_conflict("ESP32", [0, 2, 5, 12, 15])
        assert "Strapping" in result or "STRAP" in result
        assert "⚠️" in result or "WARNING" in result.upper()
    
    def test_esp32_adc2_wifi_warning(self):
        """ESP32 should warn about ADC2 + WiFi conflict."""
        result = check_pin_conflict("ESP32", [0, 2, 4, 12, 13])  # Multiple ADC2 pins
        assert "ADC2" in result
        assert "WiFi" in result
    
    def test_esp32_uart_warning(self):
        """ESP32 should warn about UART pins."""
        result = check_pin_conflict("ESP32", [1, 3, 4, 5])
        assert "UART" in result or "TX" in result or "RX" in result
    
    def test_arduino_uart_warning(self):
        """Arduino UNO should warn about D0/D1 UART."""
        result = check_pin_conflict("Arduino UNO", [0, 1, 2, 3])
        assert "UART" in result or "Serial" in result
        assert "D0" in result or "D1" in result
    
    def test_stm32_swd_conflict(self):
        """STM32 should flag SWD pins as critical conflict."""
        result = check_pin_conflict("STM32", [13, 14, 15])
        assert "❌" in result  # Should be a conflict, not just warning
        assert "SWD" in result or "debug" in result.lower()
        assert "PA13" in result or "PA14" in result
    
    def test_stm32_usb_warning(self):
        """STM32 should warn about USB pins."""
        result = check_pin_conflict("STM32", [11, 12])
        assert "USB" in result
        assert "⚠️" in result or "WARNING" in result.upper()
    
    def test_no_conflict_case(self):
        """Test clean pin selection with no conflicts."""
        result = check_pin_conflict("ESP32", [32, 33])  # ADC1 pins - truly safe
        assert "✅" in result or "No conflicts" in result
    
    def test_i2c_bus_info(self):
        """Should note when I2C bus pins are selected."""
        result = check_pin_conflict("ESP32", [21, 22])
        assert "I2C" in result
        assert "SDA" in result or "SCL" in result
    
    def test_invalid_pin_in_list(self):
        """Test error handling for invalid pin in list."""
        result = check_pin_conflict("ESP32", [4, 999])
        assert "❌" in result or "Invalid" in result


# ============================================================================
# GENERATE PIN DIAGRAM TESTS
# ============================================================================

class TestGeneratePinDiagram:
    """Test the generate_pin_diagram_ascii tool."""
    
    def test_esp32_diagram_structure(self):
        """ESP32 diagram should have proper structure."""
        result = generate_pin_diagram_ascii("ESP32")
        assert "ESP32" in result
        assert "Left Side" in result
        assert "Right Side" in result
        assert "GPIO" in result
        assert "STRAP" in result or "strapping" in result.lower()
    
    def test_arduino_uno_diagram(self):
        """Arduino UNO diagram should show digital and analog pins."""
        result = generate_pin_diagram_ascii("Arduino UNO")
        assert "Arduino UNO" in result
        assert "Digital" in result
        assert "Analog" in result
        assert "PWM" in result
        assert "D0" in result or "D1" in result
        assert "A0" in result or "A1" in result
    
    def test_stm32_diagram(self):
        """STM32 diagram should show ports and SWD warning."""
        result = generate_pin_diagram_ascii("STM32")
        assert "STM32" in result or "Blue Pill" in result
        assert "PA" in result  # Port A pins
        assert "PB" in result  # Port B pins
        assert "SWD" in result  # SWD warning
    
    def test_diagrams_have_warnings(self):
        """All diagrams should include important warnings."""
        for board in ["ESP32", "Arduino UNO", "STM32"]:
            result = generate_pin_diagram_ascii(board)
            assert "⚠️" in result or "WARNING" in result.upper() or "💡" in result
    
    def test_invalid_board_diagram(self):
        """Test error handling for invalid board."""
        result = generate_pin_diagram_ascii("INVALID")
        assert "❌" in result or "No diagram" in result


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple tools."""
    
    def test_esp32_safe_pin_selection(self):
        """Test finding safe pins on ESP32."""
        # Get all PWM pins
        pwm_result = find_pwm_pins("ESP32")
        assert "GPIO4" in pwm_result or "Pin 4" in pwm_result
        
        # Check ADC1 pins have no conflicts or warnings
        safe_pins = [32, 33]  # ADC1 pins
        conflict_result = check_pin_conflict("ESP32", safe_pins)
        assert "✅" in conflict_result or "No conflicts" in conflict_result
    
    def test_arduino_uno_i2c_sensor_project(self):
        """Simulate I2C sensor + PWM LED project."""
        # Find I2C pins
        i2c_result = find_i2c_pins("Arduino UNO")
        assert "A4" in i2c_result and "A5" in i2c_result
        
        # Find PWM for LED
        pwm_result = find_pwm_pins("Arduino UNO")
        assert "D3" in pwm_result or "3" in pwm_result
        
        # Check no conflicts
        pins = [3, 18, 19]  # D3 (PWM), A4 (SDA), A5 (SCL)
        conflict_result = check_pin_conflict("Arduino UNO", pins)
        assert "I2C" in conflict_result
    
    def test_stm32_avoiding_debug_pins(self):
        """Test STM32 project avoiding SWD pins."""
        # PA13/PA14 should trigger conflict
        conflict_result = check_pin_conflict("STM32", [13, 14])
        assert "❌" in conflict_result
        
        # Alternative pins should be safe
        safe_result = check_pin_conflict("STM32", [0, 1, 16, 17])
        assert "✅" in safe_result or "No conflicts" in safe_result
    
    def test_round_trip_pin_selection(self):
        """Test complete workflow: find -> inspect -> verify."""
        # 1. Find ADC pins
        adc_result = find_adc_pins("ESP32")
        assert "GPIO32" in adc_result or "Pin 32" in adc_result
        
        # 2. Get detailed info
        pin_info = get_pin_info("ESP32", 32)
        assert "ADC1" in pin_info
        assert "PWM" in pin_info
        
        # 3. Verify no conflicts
        conflict_result = check_pin_conflict("ESP32", [32, 33])
        assert "ADC1" not in conflict_result or "WiFi Compatible" in adc_result


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
