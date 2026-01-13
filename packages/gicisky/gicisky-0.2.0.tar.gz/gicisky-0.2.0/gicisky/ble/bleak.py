import asyncio
import logging

from bleak import BleakClient, BleakGATTCharacteristic, BleakScanner
from typing import Callable, Awaitable, Optional, Dict

from core.protocol import SERVICE_UUID, CHAR_CMD_UUID, CHAR_IMG_UUID
from logger.logger import GiciskyLogger, LogCategory
from .interface import BLEInterface, Advertisement


class BleakBackend(BLEInterface):
    """
    Bleak-based implementation of the BLEInterface abstraction.

    This backend handles BLE communication using the Bleak library but exposes
    a backend-agnostic interface so users can swap in another library (e.g.,
    BlueZ D-Bus or a custom GATT client) without modifying higher-level logic.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.client: Optional[BleakClient] = None
        self.on_notify: Optional[Callable[[int, bytes], Awaitable[None]]] = None
        self.logger = GiciskyLogger(logger)

    async def connect(self, mac: str):
        """Connect to a BLE device by MAC address."""
        self.client = BleakClient(mac)
        await self.client.connect()
        if not self.client.is_connected:
            self.logger.error(f"Failed to connect to {mac}", LogCategory.CONNECTION)
            raise ConnectionError(f"Failed to connect to {mac}")
        self.logger.info(f"Connected to {mac}", LogCategory.CONNECTION)

    async def write(self, characteristic: str, data: bytes, response: bool = False):
        """Write data to a characteristic."""
        if not self.client:
            self.logger.error("Not connected to a device", LogCategory.CONNECTION)
            raise RuntimeError("Not connected to a device")
        await self.client.write_gatt_char(characteristic, data, response=response)
        self.logger.debug(f"Wrote {len(data)} bytes to {characteristic}", LogCategory.DATA_TRANSFER)

    async def start_notify(self, characteristic: str, callback: Callable[[bytes], Awaitable[None]]):
        """
        Start receiving notifications from a specific characteristic.
        The callback must be an async function taking (handle, data).
        """
        if not self.client:
            self.logger.error("Not connected to a device", LogCategory.CONNECTION)
            raise RuntimeError("Not connected to a device")

        async def handler(sender: BleakGATTCharacteristic, data: bytearray):
            # Wrap bleak's callback in async-safe call
            self.logger.debug(f"Received notification from {characteristic}", LogCategory.NOTIFICATION)
            if asyncio.iscoroutinefunction(callback):
                await callback(bytes(data))
            else:
                callback(bytes(data))

        await self.client.start_notify(characteristic, handler)
        self.logger.info(f"Notifications started on {characteristic}", LogCategory.CONNECTION)

    async def disconnect(self):
        """Disconnect safely from the device."""
        if self.client:
            try:
                await self.client.disconnect()
                self.logger.info("Disconnected successfully", LogCategory.CONNECTION)
            except Exception as e:
                if e is EOFError:
                    self.logger.info("Disconnected successfully (EOF)", LogCategory.CONNECTION)
                else:
                    self.logger.error(f"Disconnect error: {e}", LogCategory.CONNECTION)
            finally:
                self.client = None

    async def scan_devices(self, mac: str = None) -> Dict[str, Advertisement]:
        ret = {}
        self.logger.info("Starting scan for devices...", LogCategory.CONNECTION)
        discovered = await BleakScanner.discover(return_adv=True)
        for device, adv in discovered.values():
            if (mac is None or mac == device.address) and SERVICE_UUID in adv.service_uuids:
                ret[device.address] = Advertisement(
                    name=device.name,
                    service_uuids=adv.service_uuids,
                    manufacturer_data=adv.manufacturer_data,
                )
        self.logger.info(f"Found {len(discovered)} devices, {len(ret)} of which are compatible", LogCategory.CONNECTION)
        return ret