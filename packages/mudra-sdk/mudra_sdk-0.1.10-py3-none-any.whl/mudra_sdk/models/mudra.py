from bleak.backends.device import BLEDevice
from mudra_sdk.models.computation_wrapper import ComputationWrapper
from mudra_sdk.models.enums import AirMouseButton, GestureType, HandType, LicenseType, FirmwareTarget
from ..service import BleService, MudraCharacteristicUUID
from ..libs import load_library
from ctypes import CDLL
from typing import Optional

import mudra_sdk.models.mudra_device as mudraDeviceModule
import requests

from ..models.callbacks import BleServiceDelegate, MudraDelegate

class Mudra(BleServiceDelegate):
    _instance = None
    _delegate: Optional[MudraDelegate] = None
    _ble_service: Optional[BleService] = None

    _mudra_devices: dict[str, mudraDeviceModule.MudraDevice] = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Mark instance as not yet initialized; used to guard __init__
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Guard against running initialization logic multiple times on the singleton
        if getattr(self, "_initialized", False):
            return

        self._native_lib: Optional[CDLL] = None
        self._load_native_library()
        self._ble_service = BleService(delegate=self)
        self._initialized = True

       
    def get_license_for_email_from_cloud(self, email):
        url = ComputationWrapper.get_licenses_request_url()
        payload = {"email": email}
        try:
            response = requests.post(url, json=payload)
            # Parse the JSON response
            resp_json = response.json()
            # Iterate through all possible License items
            for license_item in LicenseType:
                key = ComputationWrapper.get_licenses_key(license_item.value)
                # Check if the key exists in response and its value is True
                if key in resp_json and resp_json[key] is True:
                    ComputationWrapper.set_license(license_item.value, key)
                    print(f"Set license: {license_item.name} with key: {key}")
                else:
                    print(f"License: {license_item.name}, Key: {key} not present or not True")
            return response
        except Exception as e:
            print("Request failed:", e)
            return None


    def _load_native_library(self):
        """
        Load the native library for the current platform.
        This will automatically detect the platform and load the correct .dll/.so/.dylib
        """
        try:
            self._native_lib = load_library('MudraSDK', 'MudraSDK')
            print(f"Native library loaded: {self._native_lib}")
        except (FileNotFoundError, OSError) as e:
            # Handle the case where the library is not found or cannot be loaded
            print(f"Warning: Could not load native library: {e}")
            self._native_lib = None

    @property
    def native_lib(self) -> Optional[CDLL]:
        """Get the loaded native library, or None if not loaded."""
        return self._native_lib

    def get_native_library(self) -> Optional[CDLL]:
        return self._native_lib

    async def send_general_command(self, device: mudraDeviceModule.MudraDevice, command: bytes):
        await self._ble_service.send_general_command(device, command)

    def get_firmware_command(self, command: int) -> bytes:
        return ComputationWrapper.get_firmware_command_bytes(command)

    ### ----------------------- Connection Methods ----------------------- ###

    async def connect(self, device: mudraDeviceModule.MudraDevice):
        await self._ble_service.connect(device)

    async def disconnect(self, device: mudraDeviceModule.MudraDevice):
        await self._ble_service.disconnect(device)

    ### ----------------------- Scan Methods ----------------------- ###

    async def scan(self):
        await self._ble_service.scan()

    async def stop_scan(self):
        await self._ble_service.stop_scanning()
        
    ### ----------------------- Setter Methods ----------------------- ###
    async def set_firmware_target(self, device: mudraDeviceModule.MudraDevice, firmware_target: FirmwareTarget, active: bool):
        await self._ble_service.set_firmware_target(device, firmware_target, active)

    async def set_hand(self, device: mudraDeviceModule.MudraDevice, hand_type: HandType):
        await self._ble_service.set_hand(device, hand_type)
        
    # --- Implementation of BleServiceDelegate abstract methods ---
    def on_ble_characteristic_discovered(self, device: mudraDeviceModule.MudraDevice, characteristic_uuid: MudraCharacteristicUUID):
        if device.address in self._mudra_devices:
            print(f"on_ble_characteristic_discovered: {device.name}")
            self._mudra_devices[device.address].on_characteristic_discovered(characteristic_uuid)
        else:
            print(f"on_ble_characteristic_discovered: Device not found: {device.name}")

    def on_pressure_data_received(self, device_address: str, pressure_data: int):
        if device_address in self._mudra_devices:
            self._mudra_devices[device_address].on_pressure_data_received(pressure_data)

    def on_gesture_data_received(self, device_address: str, gesture_type: GestureType):
        if device_address in self._mudra_devices:
            self._mudra_devices[device_address].on_gesture_data_received(gesture_type)

    def on_airmouse_button_changed_received(self, device_address: str, airmouse_button: AirMouseButton):
        if device_address in self._mudra_devices:
            self._mudra_devices[device_address].on_airmouse_button_changed_received(airmouse_button)

    def on_firmware_status_updated(self, device_address: str, data: bytes):
        if device_address in self._mudra_devices:
            self._mudra_devices[device_address].on_firmware_status_updated(data)

    def handle_snc(self, device_address: str, data: bytes):
        if device_address in self._mudra_devices:
            self._mudra_devices[device_address].handle_snc(data)

    def handle_imu(self, device_address: str, data: bytes):
        if device_address in self._mudra_devices:
            self._mudra_devices[device_address].handle_imu(data)

    def on_navigation_delta_received(self, device_address: str, delta_x: int, delta_y: int):
        if device_address in self._mudra_devices:
            self._mudra_devices[device_address].on_navigation_delta_received(delta_x, delta_y)

    # --- Implementation of MudraDelegate abstract methods ---
    
    def _create_device(self, device: BLEDevice) -> mudraDeviceModule.MudraDevice:
        if device.address in self._mudra_devices:
            return self._mudra_devices[device.address]
        mudra_device = mudraDeviceModule.MudraDevice(device)
        self._mudra_devices[device.address] = mudra_device
        return mudra_device

    def set_delegate(self, delegate: MudraDelegate):
        self._delegate = delegate

    def on_device_discovered(self, device: BLEDevice):
        mudra_device = self._create_device(device)
        if self._delegate:
            self._delegate.on_device_discovered(mudra_device)

    def on_mudra_device_disconnected(self, device: BLEDevice):
        mudra_device = self._mudra_devices[device.address]
        if mudra_device and self._delegate:
            self._delegate.on_mudra_device_disconnected(device)

    def on_mudra_device_disconnecting(self, device: BLEDevice):
        mudra_device = self._mudra_devices[device.address]
        if mudra_device and self._delegate:
            self._delegate.on_mudra_device_disconnecting(device)

    def on_mudra_device_connected(self, device: BLEDevice):
        mudra_device = self._mudra_devices[device.address]
        if mudra_device and self._delegate:
            self._delegate.on_mudra_device_connected(device)

    def on_mudra_device_connecting(self, device: BLEDevice):
        mudra_device = self._mudra_devices[device.address]
        if mudra_device and self._delegate:
            self._delegate.on_mudra_device_connecting(device)

    def on_mudra_device_connection_failed(self, device: BLEDevice, error: str):
        mudra_device = self._mudra_devices[device.address]
        if mudra_device and self._delegate:
            self._delegate.on_mudra_device_connection_failed(device, error)

    def on_bluetooth_state_changed(self, state: bool):
        if self._delegate:
            self._delegate.on_bluetooth_state_changed(state)

