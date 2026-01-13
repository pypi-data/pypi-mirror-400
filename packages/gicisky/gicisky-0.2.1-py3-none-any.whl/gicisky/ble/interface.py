import dataclasses
from abc import ABC, abstractmethod
from typing import Callable, Awaitable, TypedDict, Dict

@dataclasses.dataclass
class Advertisement:
    """
    BLE advertisement data.
    """
    name: str
    manufacturer_data: {int: bytes}
    service_uuids: list[str]

class BLEInterface(ABC):
    @abstractmethod
    async def connect(self, mac: str):
        pass

    @abstractmethod
    async def write(self, characteristic: str, data: bytes, response: bool = False):
        pass

    @abstractmethod
    async def start_notify(self, characteristic: str, callback: Callable[[bytes], Awaitable[None]]):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def scan_devices(self, mac: str = None) -> Dict[str, Advertisement]:
        """
        Scan for compatible devices and get their BLE advertisement data. A device is considered compatible when it
        advertises the service UUID specified in core.protocol.SERVICE_UUID.
        This function uses BLE advertisements, which are rarely available when the device is connected!

        Args:
            mac: Optional MAC address to filter results

        Returns:
            A dictionary with MAC address as key, advertisement data as value. Only compatible devices matching the
            MAC (if specified) are returned.
        """
        pass
