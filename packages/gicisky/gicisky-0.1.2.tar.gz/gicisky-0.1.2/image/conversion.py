import dataclasses
from typing import Tuple, Dict, List

import numpy as np
from PIL import Image


@dataclasses.dataclass
class DeviceSpec:
    model: str
    size: Tuple[int, int]
    mirror: bool = False
    rotation: bool = False
    second_color: bool = True
    tft: bool = False
    compression: bool = False
    max_voltage: float = 2.9
    min_voltage: float = 2.2

ModelId = int

DEVICE_SPECS: Dict[ModelId, DeviceSpec] = {
    0x0B: DeviceSpec(
        model="EPD 2.1\" BWR",
        size=(250, 122)
    ),
    0x33: DeviceSpec(
        model="EPD 2.9\" BWR",
        size=(296, 128),
        mirror=True,
        max_voltage=3.0
    ),
    0x4B: DeviceSpec(
        model="EPD 4.2\" BWR",
        size=(400, 300),
        rotation=True,
        max_voltage=3.0
    ),
    0x2B: DeviceSpec(
        model="EPD 7.5\" BWR",
        size=(800, 480),
        mirror=True,
        rotation=True,
        compression=True,
        max_voltage=3.0
    ),
    0xA0: DeviceSpec(
        model="TFT 2.1\" BW",
        size=(250, 132),
        second_color=False,
        tft=True
    )
}

def convert_to_gicisky_bytes(img: Image.Image, model: ModelId, lum_threshold: int = 128, red_threshold: int = 170) -> bytes:
    """
    Process image according to Gicisky device specifications.
    Usage with image.optimize is recommended.

    Args:
        img: PIL Image to process
        model: Device model identifier
        lum_threshold: Luminance threshold for black/white conversion
        red_threshold: Threshold for red color detection

    Returns:
        bytes: Processed image data in Gicisky format
    """

    specs = DEVICE_SPECS.get(model)
    if not specs:
        raise ValueError("Unknown model")

    width, height = specs.size
    img = img.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)

    if specs.tft:
        # Resize to half width and double height
        img = img.resize((width // 2, height * 2), Image.Resampling.LANCZOS)
        width, height = img.size
    if specs.mirror:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

    arr = np.array(img)

    # Process pixels - column-major order
    byte_data, red_byte_data = [], []
    current_byte, current_red_byte = 0, 0
    bit_position = 7

    for x in range(width):
        for y in range(height):
            r, g, b = arr[y, x]  # Note: numpy uses [y, x] indexing
            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

            if specs.compression:
                # When compression is enabled, dark pixels set bits
                if luminance < lum_threshold:
                    current_byte |= (1 << bit_position)
            else:
                # When compression is disabled, light pixels set bits
                if luminance > lum_threshold:
                    current_byte |= (1 << bit_position)

            # Red color detection
            if r > red_threshold and g < red_threshold:
                current_red_byte |= (1 << bit_position)

            bit_position -= 1
            if bit_position < 0:
                byte_data.append(current_byte)
                red_byte_data.append(current_red_byte)
                current_byte, current_red_byte = 0, 0
                bit_position = 7

    # Handle remaining bits
    if bit_position != 7:
        byte_data.append(current_byte)
        red_byte_data.append(current_red_byte)

    if specs.compression:
        byte_data_compressed = _apply_compression(byte_data, red_byte_data, width, height, specs.second_color)
    else:
        # Simple concatenation when compression is disabled
        byte_data_compressed = byte_data[:]
        if specs.second_color:
            byte_data_compressed.extend(red_byte_data)

    return bytes(byte_data_compressed)


def _apply_compression(byte_data: List[int], red_byte_data: List[int],
                       width: int, height: int, second_color: bool) -> List[int]:
    """
    Apply compression algorithm

    Args:
        byte_data: Black/white pixel data
        red_byte_data: Red pixel data
        width: Image width
        height: Image height
        second_color: Whether to include second color (red) data

    Returns:
        List[int]: Compressed byte data
    """
    byte_data_compressed = [0x00, 0x00, 0x00, 0x00]  # Header
    byte_per_line = height // 8
    current_pos = 0

    for i in range(width):
        # Add line header
        byte_data_compressed.extend([
            0x75,
            byte_per_line + 7,
            byte_per_line,
            0x00,
            0x00,
            0x00,
            0x00
        ])

        # Add pixel data for this line
        for b in range(byte_per_line):
            if current_pos < len(byte_data):
                byte_data_compressed.append(byte_data[current_pos])
            else:
                byte_data_compressed.append(0x00)  # Padding
            current_pos += 1

    # Process red data if enabled
    if second_color:
        current_pos = 0
        for i in range(width):
            # Add line header
            byte_data_compressed.extend([
                0x75,
                byte_per_line + 7,
                byte_per_line,
                0x00,
                0x00,
                0x00,
                0x00
            ])

            # Add pixel data for this line
            for b in range(byte_per_line):
                if current_pos < len(red_byte_data):
                    byte_data_compressed.append(red_byte_data[current_pos])
                else:
                    byte_data_compressed.append(0x00)  # Padding
                current_pos += 1

    # Update header with total length
    total_length = len(byte_data_compressed)
    byte_data_compressed[0] = total_length & 0xff
    byte_data_compressed[1] = (total_length >> 8) & 0xff
    byte_data_compressed[2] = (total_length >> 16) & 0xff
    byte_data_compressed[3] = (total_length >> 24) & 0xff

    return byte_data_compressed
