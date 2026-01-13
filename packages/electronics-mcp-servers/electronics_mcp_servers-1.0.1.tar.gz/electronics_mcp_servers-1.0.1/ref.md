Ohm 定律計算器 MCP ⭐⭐⭐⭐
難度：簡單 | 時間：3 小時 | 實用性：高

python
@mcp.tool()
def ohms_law_calculate(known_value: str, known_unit: str, target_unit: str) -> str:
    """使用 Ohm 定律 V = I × R 計算未知值。
    
    Args:
        known_value: 已知值（例如："1.5"）
        known_unit: 已知值單位（"V" for 電壓, "A" for 電流, "Ω" for 阻值）
        target_unit: 要求的單位（例如："Ω"）
    
    Examples:
        "1.5", "A", "Ω" + "R=100Ω" → "V = 150V"
    """

GPIO 引腳速查表 MCP ⭐⭐⭐⭐
難度：簡單 | 時間：3-4 小時 | 實用性：極高

你可以建立：

text
工具集:
├─ get_pin_info(board_type: str, pin_number: int)
│  → 查詢 GPIO 引腳功能
│  → 例："ESP32, 5" → "GPIO5, PWM, I2C SDA 可選"
│
├─ find_pwm_pins(board_type)
│  → 列出所有支持 PWM 的引腳
│
├─ find_adc_pins(board_type)
│  → 列出所有 ADC 輸入引腳
│
├─ check_pin_conflict(board_type, pin_list)
│  → 檢查多個引腳是否功能衝突
│
└─ generate_pin_diagram_ascii(board_type)
   → 生成 ASCII 引腳圖
為什麼很棒：

✅ 數據庫式工具（易於實現）

✅ 解決嵌入式開發者的真實痛點

✅ 支持多板型（Arduino、ESP32、STM32）

✅ 可整合官方數據表

實現例子：

python
from fastmcp import FastMCP

mcp = FastMCP("GPIO Pin Reference")

# 引腳數據庫
PIN_DATABASE = {
    "ESP32": {
        0: {"name": "GPIO0", "features": ["Bootstrap", "JTAG", "ADC2_1"], "notes": "開機須低電平"},
        1: {"name": "GPIO1", "features": ["UART0_TXD", "JTAG", "ADC2_2"]},
        2: {"name": "GPIO2", "features": ["ADC2_3", "JTAG"]},
        # ... 更多引腳
    },
    "Arduino UNO": {
        0: {"name": "RX", "features": ["UART"]},
        1: {"name": "TX", "features": ["UART"]},
        # ... 更多引腳
    }
}

@mcp.tool()
def get_pin_info(board_type: str, pin_number: int) -> str:
    """查詢特定開發板的引腳資訊。"""
    if board_type not in PIN_DATABASE:
        return f"✗ 不支持的開發板：{board_type}"
    
    board_pins = PIN_DATABASE[board_type]
    if pin_number not in board_pins:
        return f"✗ 引腳不存在：{pin_number}"
    
    pin_info = board_pins[pin_number]
    result = f"【{pin_info['name']}】\n"
    result += f"功能：{', '.join(pin_info['features'])}\n"
    if 'notes' in pin_info:
        result += f"注意：{pin_info['notes']}\n"
    
    return result

@mcp.tool()
def find_pwm_pins(board_type: str) -> str:
    """列出開發板所有 PWM 引腳。"""
    if board_type not in PIN_DATABASE:
        return f"✗ 不支持的開發板"
    
    pwm_pins = []
    for pin_num, pin_info in PIN_DATABASE[board_type].items():
        if any("PWM" in f or "Timer" in f for f in pin_info.get("features", [])):
            pwm_pins.append(f"Pin {pin_num} ({pin_info['name']})")
    
    return "【PWM 引腳】\n" + "\n".join(pwm_pins) if pwm_pins else "無 PWM 引腳"

電容器計算工具 MCP ⭐⭐⭐⭐
難度：簡單 | 時間：4-5 小時 | 實用性：高

你可以建立：

text
工具集:
├─ calculate_capacitive_reactance(capacitance_f, frequency_hz)
│  → 計算容抗 Xc = 1 / (2π × f × C)
│
├─ calculate_rc_time_constant(resistance_ohm, capacitance_f)
│  → 計算 RC 時間常數 τ = R × C
│
├─ calculate_resonant_frequency(inductance_h, capacitance_f)
│  → 計算共振頻率 f = 1 / (2π√(LC))
│
└─ suggest_capacitor_for_filter(target_frequency, resistance_ohm)
   → 推薦合適的電容值用於 RC 濾波器
為什麼很棒：

✅ 數學公式簡單明確

✅ 硬體設計常用工具

✅ 多個相關工具可以擴展

✅ 有真實電路設計場景

關鍵公式：

python
import math

@mcp.tool()
def calculate_capacitive_reactance(capacitance_f: float, frequency_hz: float) -> str:
    """計算電容器的容抗。
    
    公式：Xc = 1 / (2π × f × C)
    """
    if frequency_hz <= 0 or capacitance_f <= 0:
        return "✗ 頻率和電容必須為正數"
    
    xc = 1 / (2 * math.pi * frequency_hz * capacitance_f)
    
    return f"容抗 (Xc) = {xc:.2f}Ω @ {frequency_hz}Hz"

@mcp.tool()
def calculate_rc_time_constant(resistance_ohm: float, capacitance_f: float) -> str:
    """計算 RC 電路時間常數 τ = R × C"""
    tau = resistance_ohm * capacitance_f
    
    if tau < 0.001:
        return f"時間常數 τ = {tau*1e6:.2f}µs"
    elif tau < 1:
        return f"時間常數 τ = {tau*1e3:.2f}ms"
    else:
        return f"時間常數 τ = {tau:.2f}s"

電阻色碼解碼器 MCP ⭐⭐⭐⭐⭐
難度：極簡 | 時間：3-4 小時 | 實用性：高

你可以建立：

text
工具集:
├─ decode_resistor_color_bands(color1, color2, color3, [tolerance])
│  → 輸入："Brown, Black, Red, Gold"
│  → 輸出：1000Ω ±5%
│
├─ encode_resistor_value(resistance_ohm, tolerance)
│  → 輸入：4700Ω, 5%
│  → 輸出：色帶序列
│
└─ find_standard_resistor(target_ohm, tolerance, available_series)
   → 推薦最接近的標準阻值（E12、E24 系列）
為什麼很棒：

✅ 純粹的資料轉換邏輯（零硬體依賴）

✅ 開發超快（< 50 行 Python 代碼）

✅ 實用：每個硬體工程師都會用

✅ 易於測試和驗證

代碼框架：

python
from fastmcp import FastMCP

mcp = FastMCP("Resistor Decoder")

# 色碼對應表
COLOR_VALUES = {
    "Black": 0, "Brown": 1, "Red": 2, "Orange": 3,
    "Yellow": 4, "Green": 5, "Blue": 6, "Violet": 7,
    "Grey": 8, "White": 9
}

MULTIPLIERS = {
    "Black": 1, "Brown": 10, "Red": 100, "Orange": 1000,
    "Yellow": 10000, "Green": 100000, "Blue": 1000000
}

@mcp.tool()
def decode_resistor_color_bands(band1: str, band2: str, band3: str, tolerance: str = "Brown") -> str:
    """解碼電阻色碼。
    
    Args:
        band1: 首位色環（有效值：Black-White）
        band2: 次位色環
        band3: 倍數色環（或第三位数字）
        tolerance: 容差色環（預設：Brown = ±1%）
    
    Returns:
        阻值與容差描述
    """
    try:
        first_digit = COLOR_VALUES[band1]
        second_digit = COLOR_VALUES[band2]
        multiplier = MULTIPLIERS[band3]
        
        resistance = (first_digit * 10 + second_digit) * multiplier
        
        tolerance_map = {"Brown": "±1%", "Red": "±2%", "Gold": "±5%", "Silver": "±10%"}
        tolerance_str = tolerance_map.get(tolerance, "±1%")
        
        # 格式化阻值
        if resistance < 1000:
            return f"{resistance}Ω {tolerance_str}"
        elif resistance < 1000000:
            return f"{resistance/1000:.1f}kΩ {tolerance_str}"
        else:
            return f"{resistance/1000000:.1f}MΩ {tolerance_str}"
    
    except KeyError as e:
        return f"✗ 無效的色碼：{str(e)}"

if __name__ == "__main__":
    mcp.run()
測試它：

bash
# Claude 對話
你："解碼棕黑紅金色的電阻"
Claude 應該回應："1000Ω ±5%"