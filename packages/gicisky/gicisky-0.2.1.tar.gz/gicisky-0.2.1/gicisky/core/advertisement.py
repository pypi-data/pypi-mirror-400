import dataclasses

from ..ble.interface import Advertisement
from ..image.conversion import DEVICE_SPECS, DeviceSpec, ModelId


@dataclasses.dataclass
class DeviceData:
    name: str
    model: ModelId
    firmware: int
    hardware: int
    battery: float
    voltage: float

def parse_advertisement(adv: Advertisement) -> DeviceData:

    data = adv.manufacturer_data[0x5053]
    device_id = data[0]
    volt = data[1] / 10
    firmware = (data[2] << 8) + data[3]
    hardware = (data[0] << 8) + data[4]

    device = DEVICE_SPECS[device_id]

    return DeviceData(
        name=adv.name,
        model=device_id,
        firmware=firmware,
        hardware=hardware,
        battery=(volt - device.min_voltage) * 100 / (device.max_voltage - device.min_voltage),
        voltage=volt
    )