# Mudra API Python

Python SDK for Mudra with native library support. This SDK enables you to connect to and interact with Mudra devices via Bluetooth Low Energy (BLE).

For more detailed documentation, visit: [https://wearable-devices.github.io/#welcome](https://wearable-devices.github.io/#welcome)

## Features

- 🔌 **Bluetooth Low Energy (BLE) Support** - Connect to Mudra devices wirelessly
- 📱 **Cross-Platform** - Supports Windows, macOS
- 🎯 **Device Discovery** - Scan and discover nearby Mudra devices
- 📊 **Multiple Sensor Data Types** - SNC, IMU (Accelerometer/Gyroscope), Pressure, Navigation, Gestures
- 🎮 **Firmware Targets** - Control where data is sent (App, HID)
- 🤚 **Hand Configuration** - Set device for left or right hand
- 🔄 **Event-Driven Architecture** - Use delegates for handling device events
- 🔐 **Cloud License Management** - Retrieve licenses from cloud

## Requirements

- Python 3.7 or higher
- Bluetooth-enabled computer
- Mudra device

## Installation

```bash
pip install mudra-sdk
```

## Platform Support

The SDK includes native libraries for the following platforms:

- **Windows**
- **macOS**

The appropriate library is automatically loaded based on your platform.

## API Reference

### Mudra Class

Main entry point for the SDK.

- [`scan()`](#scanning-for-devices) - Start scanning for Mudra devices (async)
- [`stop_scan()`](#scanning-for-devices) - Stop scanning for devices (async)
- [`set_delegate(delegate: MudraDelegate)`](#basic-setup) - Set the delegate for handling device events
- [`get_license_for_email_from_cloud(email: str)`](#basic-setup) - Retrieve licenses from cloud for the given email

### MudraDevice Class

Represents a discovered or connected Mudra device.

#### Connection Methods
- `connect()` - Connect to the device (async)
- `disconnect()` - Disconnect from the device (async)

#### Data Feature Callbacks
All data callbacks can be enabled by passing a callback function, or disabled by passing `None`.

- `set_on_snc_ready(callback)` - Enable/disable SNC (Sensor Neural Control) data (async)
  - Callback signature: `(timestamp: int, data_list: List[float], frequency: int, frequency_std: float, rms_list: List[float]) -> None`
  
- `set_on_imu_acc_ready(callback)` - Enable/disable IMU Accelerometer data (async)
  - Callback signature: `(timestamp: int, data_list: List[float], frequency: int, frequency_std: float, rms_list: List[float]) -> None`
  
- `set_on_imu_gyro_ready(callback)` - Enable/disable IMU Gyroscope data (async)
  - Callback signature: `(timestamp: int, data_list: List[float], frequency: int, frequency_std: float, rms_list: List[float]) -> None`
  
- `set_on_pressure_ready(callback)` - Enable/disable pressure sensing (async)
  - Callback signature: `(pressure_data: int) -> None`
  - Pressure values range from 0 to 100
  
- `set_on_navigation_ready(callback)` - Enable/disable navigation delta data (async)
  - Callback signature: `(delta_x: int, delta_y: int) -> None`
  
- `set_on_gesture_ready(callback)` - Enable/disable gesture recognition (async)
  - Callback signature: `(gesture_type: GestureType) -> None`
  
- `set_on_button_changed(callback)` - Enable/disable Air Touch Button change notifications (async)
  - Callback signature: `(air_touch_button: AirMouseButton) -> None`

#### Firmware Configuration
- `set_firmware_target(target: FirmwareTarget, active: bool)` - Enable/disable firmware targets (async)
  - Targets: `FirmwareTarget.navigation_to_app`, `FirmwareTarget.gesture_to_hid`, `FirmwareTarget.navigation_to_hid`
  
- `set_hand(hand_type: HandType)` - Set device hand configuration (async)
  - Options: `HandType.left`, `HandType.right`
  
- `set_air_touch_active(active: bool)` - Enable/disable embedded AirTouch feature (async)

#### Device Properties
- `firmware_status` - Access to `FirmwareStatus` object with current device state
  - Properties include: `is_snc_enabled`, `is_acc_enabled`, `is_gyro_enabled`, `is_pressure_enabled`, `is_navigation_enabled`, `is_gesture_enabled`, `is_air_touch_enabled`, `is_sends_navigation_to_app_enabled`, `is_sends_gesture_to_hid_enabled`, `is_sends_navigation_to_hid_enabled`

### MudraDelegate Interface

Implement this interface to handle device events:

- `on_device_discovered(device: MudraDevice)` - Called when a device is discovered
- `on_mudra_device_connected(device: MudraDevice)` - Called when a device connects
- `on_mudra_device_disconnected(device: MudraDevice)` - Called when a device disconnects
- `on_mudra_device_connecting(device: MudraDevice)` - Called when a device is connecting
- `on_mudra_device_disconnecting(device: MudraDevice)` - Called when a device is disconnecting
- `on_mudra_device_connection_failed(device: MudraDevice, error: str)` - Called when connection fails
- `on_bluetooth_state_changed(state: bool)` - Called when Bluetooth state changes

### Enums

- `FirmwareTarget` - Firmware target options: `navigation_to_app`, `gesture_to_hid`, `navigation_to_hid`
- `HandType` - Hand configuration: `left`, `right`
- `GestureType` - Gesture recognition types
- `AirMouseButton` - Air Touch Button states


## Getting Started

### Basic Setup

```python
import asyncio
from mudra_sdk import Mudra, MudraDevice
from mudra_sdk.models.callbacks import MudraDelegate

# Create Mudra instance
mudra = Mudra()

# Retrieve license from cloud (required for full functionality)
mudra.get_license_for_email_from_cloud("your-email@example.com")

# Implement delegate to handle device events
class MyMudraDelegate(MudraDelegate):
    def on_device_discovered(self, device: MudraDevice):
        print(f"Discovered: {device.name} ({device.address})")

    def on_mudra_device_connected(self, device: MudraDevice):
        print(f"Device connected: {device.name}")

    def on_mudra_device_disconnected(self, device: MudraDevice):
        print(f"Device disconnected: {device.name}")

    def on_mudra_device_connecting(self, device: MudraDevice):
        print(f"Device connecting: {device.name}...")

    def on_mudra_device_disconnecting(self, device: MudraDevice):
        print(f"Device disconnecting: {device.name}...")

    def on_mudra_device_connection_failed(self, device: MudraDevice, error: str):
        print(f"Connection failed: {device.name}, Error: {error}")

    def on_bluetooth_state_changed(self, state: bool):
        print(f"Bluetooth state changed: {'On' if state else 'Off'}")

# Set the delegate
mudra.set_delegate(MyMudraDelegate())
```

### Scanning for Devices

```python
mudra = Mudra()

async def start():
    mudra.set_delegate(MyMudraDelegate())
    
    # Start scanning for Mudra devices
    await mudra.scan()
    
    # Wait for devices to be discovered
    await asyncio.sleep(10)

async def stop():
    # Stop scanning when done
    await mudra.stop_scan()
```

### Connecting to a Device

```python
# Store discovered devices
discovered_devices = []

class MyMudraDelegate(MudraDelegate):
    def on_device_discovered(self, device: MudraDevice):
        discovered_devices.append(device)
        print(f"Discovered: {device.name}")

async def main():
    mudra = Mudra()
    mudra.set_delegate(MyMudraDelegate())
    
    # Start scanning
    await mudra.scan()
    await asyncio.sleep(5)  # Wait for discovery
    
    # Connect to the first discovered device
    if discovered_devices:
        device = discovered_devices[0]
        await device.connect()
        print(f"Connected to {device.name}")
        
        # ... use the device ...
        
        # Disconnect when done
        await device.disconnect()

asyncio.run(main())
```

## Usage Examples

### SNC (Sensor Neural Control) Data

Enable SNC data to receive neural control signals with RMS values:

```python
def on_snc_ready(timestamp: int, data_list: list, frequency: int, frequency_std: float, rms_list: list):
    print(f"SNC - Frequency: {frequency} Hz, RMS: {rms_list}")

async def enable_snc():
    await device.set_on_snc_ready(on_snc_ready)

async def disable_snc():
    await device.set_on_snc_ready(None)
```

### IMU Data (Accelerometer & Gyroscope)

Enable IMU data to receive motion sensor information:

```python
def on_imu_acc_ready(timestamp: int, data_list: list, frequency: int, frequency_std: float, rms_list: list):
    print(f"IMU Acc - Frequency: {frequency:.2f} Hz")

def on_imu_gyro_ready(timestamp: int, data_list: list, frequency: int, frequency_std: float, rms_list: list):
    print(f"IMU Gyro - Frequency: {frequency:.2f} Hz")

async def enable_imu():
    await device.set_on_imu_acc_ready(on_imu_acc_ready)
    await device.set_on_imu_gyro_ready(on_imu_gyro_ready)

async def disable_imu():
    await device.set_on_imu_acc_ready(None)
    await device.set_on_imu_gyro_ready(None)
```

### Pressure Data

Enable pressure sensing to receive real-time pressure data from the device:

```python
def on_pressure_ready(pressure_data: int):
    print(f"Pressure: {pressure_data}")  # Range: 0-100

async def enable_pressure():    
    await device.set_on_pressure_ready(on_pressure_ready)

async def disable_pressure():
    await device.set_on_pressure_ready(None)
```

### Navigation Data

Enable navigation to receive cursor movement deltas:

```python
def on_navigation_ready(delta_x: int, delta_y: int):
    print(f"Navigation delta: X={delta_x}, Y={delta_y}")

async def enable_navigation():
    await device.set_on_navigation_ready(on_navigation_ready)

async def disable_navigation():
    await device.set_on_navigation_ready(None)
```

### Gesture Recognition

Enable gesture recognition to detect hand gestures:

```python
from mudra_sdk.models.enums import GestureType

def on_gesture_ready(gesture_type: GestureType):
    print(f"Gesture detected: {gesture_type}")

async def enable_gesture():
    await device.set_on_gesture_ready(on_gesture_ready)

async def disable_gesture():
    await device.set_on_gesture_ready(None)
```

### Air Touch Button

Monitor Air Touch Button state changes:

```python
from mudra_sdk.models.enums import AirMouseButton

def on_button_changed(air_touch_button: AirMouseButton):
    print(f"Air Touch Button: {air_touch_button}")

async def enable_button_monitoring():
    await device.set_on_button_changed(on_button_changed)

async def disable_button_monitoring():
    await device.set_on_button_changed(None)
```

### Firmware Targets

Control where firmware sends data (to your app or to HID):

```python
from mudra_sdk.models.enums import FirmwareTarget

async def configure_firmware_targets():
    # Enable navigation data to be sent to your app
    await device.set_firmware_target(FirmwareTarget.navigation_to_app, True)
    
    # Enable gesture data to be sent to HID (Human Interface Device)
    await device.set_firmware_target(FirmwareTarget.gesture_to_hid, True)
    
    # Enable navigation data to be sent to HID
    await device.set_firmware_target(FirmwareTarget.navigation_to_hid, True)

async def disable_firmware_targets():
    await device.set_firmware_target(FirmwareTarget.navigation_to_app, False)
    await device.set_firmware_target(FirmwareTarget.gesture_to_hid, False)
    await device.set_firmware_target(FirmwareTarget.navigation_to_hid, False)
```

### Hand Configuration

Set the device for left or right hand:

```python
from mudra_sdk.models.enums import HandType

async def set_hand_configuration():
    # Set for left hand
    await device.set_hand(HandType.left)
    
    # Or set for right hand
    await device.set_hand(HandType.right)
```

### Embedded AirTouch

Enable/disable the embedded AirTouch feature:

```python
async def enable_embedded_airtouch():
    await device.set_air_touch_active(True)

async def disable_embedded_airtouch():
    await device.set_air_touch_active(False)
```

### Device Discovery

Discover GATT services and characteristics on a connected device:

```python
async def discover_device():
    await mudra.ble_service.discover_services_and_characteristics(device)
    print("Device discovery completed")
```

### Checking Device Status

Access the device's firmware status to check which features are enabled:

```python
# After connecting to a device
if device.firmware_status.is_pressure_enabled:
    print("Pressure sensing is enabled")

if device.firmware_status.is_navigation_enabled:
    print("Navigation is enabled")

if device.firmware_status.is_sends_navigation_to_app_enabled:
    print("Navigation data is being sent to app")
```

## Support
For issues, questions, or contributions please contact [support@mudra-band.com](mailto:support@mudra-band.com)
