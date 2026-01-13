# DFRobot ID809 MicroPython Driver

[![PyPI version](https://badge.fury.io/py/SEN0359.svg)](https://badge.fury.io/py/SEN0359)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MicroPython driver for the **DFRobot SEN0359** capacitive fingerprint sensor (ID809).

This is a direct port of the official [DFRobot_ID809](https://github.com/DFRobot/DFRobot_ID809) C++ library to MicroPython.

## Features

-  Full I2C communication support
-  Fingerprint enrollment (up to 80 fingerprints)
-  Fingerprint verification and search
-  LED control (colors and modes)
-  Device configuration (security level, duplicate check, self-learning)
-  Low power sleep mode
-  Comprehensive error handling

## Hardware

- **Sensor**: [DFRobot SEN0359](https://www.dfrobot.com/product-2165.html) 
- **Capacitive Fingerprint Sensor**: 80 
- **Interface**: I2C (default address: 0x1F)
- **Voltage**: 3.3V / 5V compatible

## Installation

### From PyPI (recomendado)

```bash
pip install SEN0359
```

### Con dependencias de desarrollo (para PC)

```bash
# Incluye stubs para autocompletado en IDE + herramientas de testing
pip install SEN0359[dev]

# Solo stubs para ESP32
pip install SEN0359[stubs-esp32]

# Solo stubs para Raspberry Pi Pico (RP2)
pip install SEN0359[stubs-rp2]
```

### Manual Installation (MicroPython)

Copy the `dfrobot_id809` folder to your MicroPython device's `lib` directory.

> **Nota**: El módulo `machine` viene integrado en MicroPython y no necesita instalarse por separado.

## Wiring

| Sensor Pin | ESP32 Pin | Description |
|------------|-----------|-------------|
| VCC        | 3.3V/5V   | Power       |
| GND        | GND       | Ground      |
| SDA        | GPIO21    | I2C Data    |
| SCL        | GPIO22    | I2C Clock   |

## Quick Start

```python
from machine import I2C, Pin
from dfrobot_id809 import DFRobot_ID809_I2C, LEDColor, LEDMode

# Initialize I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

# Create sensor instance
sensor = DFRobot_ID809_I2C(i2c)

# Initialize sensor
if sensor.begin():
    print("Sensor initialized!")
    
    # Turn on green LED
    sensor.ctrl_led(LEDMode.KEEPS_ON, LEDColor.GREEN)
    
    # Check connection
    if sensor.is_connected():
        print("Sensor connected!")
else:
    print("Sensor initialization failed!")
```

## Usage Examples

### Enroll a Fingerprint

```python
from dfrobot_id809 import DFRobot_ID809_I2C, LEDColor, LEDMode, DELALL

def enroll_fingerprint(sensor):
    # Get first available ID
    empty_id = sensor.get_empty_id()
    if empty_id == 0:
        print("No space available!")
        return False
    
    print(f"Enrolling fingerprint at ID: {empty_id}")
    
    # Collect fingerprint 3 times
    for i in range(3):
        print(f"Place finger ({i+1}/3)...")
        sensor.ctrl_led(LEDMode.BREATHING, LEDColor.BLUE)
        
        # Wait for fingerprint
        if sensor.collection_fingerprint(timeout=10000) == 0:
            sensor.ctrl_led(LEDMode.KEEPS_ON, LEDColor.GREEN)
            print("Captured!")
            
            # Wait for finger removal
            while sensor.detect_finger():
                pass
        else:
            sensor.ctrl_led(LEDMode.KEEPS_ON, LEDColor.RED)
            print(f"Error: {sensor.get_error_description()}")
            return False
    
    # Store fingerprint
    if sensor.store_fingerprint(empty_id) == 0:
        print(f"Fingerprint stored at ID {empty_id}")
        sensor.ctrl_led(LEDMode.KEEPS_ON, LEDColor.GREEN)
        return True
    else:
        print("Storage failed!")
        sensor.ctrl_led(LEDMode.KEEPS_ON, LEDColor.RED)
        return False
```

### Verify a Fingerprint

```python
def verify_fingerprint(sensor):
    print("Place finger to verify...")
    sensor.ctrl_led(LEDMode.BREATHING, LEDColor.BLUE)
    
    # Capture fingerprint
    if sensor.collection_fingerprint(timeout=10000) == 0:
        # Search in database
        result = sensor.search()
        
        if result > 0:
            print(f"Match found! ID: {result}")
            sensor.ctrl_led(LEDMode.KEEPS_ON, LEDColor.GREEN)
            return result
        else:
            print("No match found")
            sensor.ctrl_led(LEDMode.KEEPS_ON, LEDColor.RED)
            return 0
    else:
        print(f"Capture error: {sensor.get_error_description()}")
        return -1
```

### Delete Fingerprints

```python
# Delete specific fingerprint
sensor.del_fingerprint(1)  # Delete ID 1

# Delete all fingerprints
sensor.del_fingerprint(DELALL)
```

### LED Control

```python
from dfrobot_id809 import LEDColor, LEDMode

# Solid colors
sensor.ctrl_led(LEDMode.KEEPS_ON, LEDColor.GREEN)
sensor.ctrl_led(LEDMode.KEEPS_ON, LEDColor.RED)
sensor.ctrl_led(LEDMode.KEEPS_ON, LEDColor.BLUE)

# Breathing effect
sensor.ctrl_led(LEDMode.BREATHING, LEDColor.CYAN)

# Blinking (5 times)
sensor.ctrl_led(LEDMode.FAST_BLINK, LEDColor.YELLOW, blink_count=5)

# Turn off
sensor.ctrl_led(LEDMode.NORMAL_CLOSE, LEDColor.GREEN)
```

### Device Information

```python
# Get device info
info = sensor.get_device_info()
print(f"Device info: {info}")

# Get enrolled count
count = sensor.get_enroll_count()
print(f"Enrolled fingerprints: {count}")

# Check if ID is registered
status = sensor.get_status_id(1)
print(f"ID 1 status: {'registered' if status else 'empty'}")

# Get security level (1-5)
level = sensor.get_security_level()
print(f"Security level: {level}")
```

## API Reference

### Classes

- `DFRobot_ID809_I2C` - Main sensor class for I2C communication
- `LEDMode` - LED mode constants
- `LEDColor` - LED color constants
- `Error` - Error code constants and descriptions

### Main Methods

| Method | Description |
|--------|-------------|
| `begin()` | Initialize sensor |
| `is_connected()` | Check connection |
| `detect_finger()` | Detect finger presence |
| `collection_fingerprint(timeout)` | Capture fingerprint |
| `store_fingerprint(id)` | Store captured fingerprint |
| `search()` | Search fingerprint in database |
| `verify(id)` | Verify against specific ID |
| `del_fingerprint(id)` | Delete fingerprint(s) |
| `ctrl_led(mode, color, blink_count)` | Control LED |
| `get_enroll_count()` | Get enrolled count |
| `get_empty_id()` | Get first available ID |
| `enter_sleep_state()` | Enter low power mode |

## Error Codes

```python
from dfrobot_id809 import Error

# Get error description
error_msg = Error.get_description(error_code)
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Credits

- Original C++ library: [DFRobot](https://github.com/DFRobot/DFRobot_ID809)

