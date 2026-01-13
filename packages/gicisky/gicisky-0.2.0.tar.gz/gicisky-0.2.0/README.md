# 🏷 Gicisky Python Library

[🐍 PyPi Page](https://pypi.org/project/gicisky/) - [📄 Source code](https://git.boxo.cc/massivebox/gicisky)

A Python library for interacting with Gicisky electronic ink display tags via Bluetooth Low Energy (BLE).

## ℹ️ Features

- **Advertisement parsing**: Discover compatible devices and get their info (battery level, model, hardware and software
version)
- **Image uploading**: Upload images to your ESL, with all the features it supports (including third color and compression!)
- **Bluetooth library independent**: Use the provided [Bleak backend](https://git.boxo.cc/massivebox/gicisky/src/branch/main/ble/bleak.py) or implement the [BLE Interface](https://git.boxo.cc/massivebox/gicisky/src/branch/main/ble/interface.py)
to use any other Bluetooth library.
- **Image conversion**: Provide any image and let the library convert it for you to the device's format.

## 📱 Supported Devices

- EPD 2.1" BWR (0x0B)
- EPD 2.9" BWR (0x33)
- EPD 4.2" BWR (0x4B)
- EPD 7.5" BWR (0x2B)
- TFT 2.1" BW (0xA0)

## ⬇️ Installation

```bash
pip install gicisky
```

Or install from source:

```bash
git clone https://git.boxo.cc/massivebox/gicisky
cd gicisky
pip install -r requirements.txt
```

## ▶️ Quick Start

Check out the [examples](https://git.boxo.cc/massivebox/gicisky/src/branch/main/examples)!

```bash
python3 examples/send_bleak.py ~/path/to/image.png
python3 examples/send_bleak.py --no-optimize ~/path/to/image.png # Without dithering
```

## ⚙️ Components

1. **BLE Interface** ([gicisky.ble/](https://git.boxo.cc/massivebox/gicisky/src/branch/main/gicisky/ble)): Handles Bluetooth Low Energy communication
2. **Core Protocol** ([gicisky.core/](https://git.boxo.cc/massivebox/gicisky/src/branch/main/gicisky/core)): Implements the Gicisky communication protocol, independent of the Bluetooth library
3. **Image Processing** ([gicisky.image/](https://git.boxo.cc/massivebox/gicisky/src/branch/main/gicisky/image)): `conversion` formats images to the Gicisky format, `optimizer` (optional) uses
dithering and letterboxing for better results
4. **Logging** ([gicisky.logger/](https://git.boxo.cc/massivebox/gicisky/src/branch/main/gicisky/logger)): Provides detailed logging capabilities

## ⚠️ Version 0.2.0 Migration Guide

**Breaking Change**: Starting with version 0.2.0, all components are now under the `gicisky` namespace to prevent conflicts with other packages.

### Import Changes

**Before (v0.1.x):**
```python
from ble.bleak import BleakBackend
from core.advertisement import parse_advertisement
from image import optimize
```

**After (v0.2.0+):**
```python
from gicisky.ble import BleakBackend
from gicisky.core import parse_advertisement
from gicisky.image import optimize
```

### Quick Import

For convenience, you can still use star imports to access all public APIs:

```python
from gicisky import *  # Imports: BleakBackend, parse_advertisement, optimize, etc.
```

## 🧱 Requirements

- Python 3.7+
- bleak (for BLE communication)
- PIL/Pillow (for image processing)
- numpy (for image manipulation)

Install all requirements:

```bash
pip install -r requirements.txt
```

## ❤️ Credits

- For much of the original work on the protocol: [atc1441/ATC_GICISKY_ESL](https://github.com/atc1441/ATC_GICISKY_ESL)
- For most of the advertisement parsing logic: [eigger/hass-gicisky](https://github.com/eigger/hass-gicisky)

## 🤝 Support the Project

Thanks for your interest in supporting the project.

- Help me by opening issues and creating pull requests: all contributions are welcome!
- If you want to contribute financially, take a look [here](https://boxo.cc/pages/donate/). Thanks a lot!
- If you haven't bought your Gigisky ESL yet, please buy it through my [AliExpress affiliate link](https://s.click.aliexpress.com/e/_c2IOUkF5).
I will earn a small commission from your order, but it will not cost you anything. Thanks!

## 📚 License

MIT License