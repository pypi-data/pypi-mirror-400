from PIL import Image
import numpy as np
from typing import Tuple
from .conversion import DEVICE_SPECS, ModelId, DeviceSpec


def optimize(img: Image.Image, model: ModelId) -> Image.Image:
    """
    Optimize an image for a specific Gicisky device model.
    
    Args:
        img: Input PIL Image
        model: Device model identifier
        
    Returns:
        Image.Image: Optimized image
    """
    specs: DeviceSpec = DEVICE_SPECS.get(model)
    if not specs:
        raise ValueError(f"Unknown model: {model}")
    target_width, target_height = specs.size

    canvas = Image.new("RGB", (target_width, target_height), color="white")
    img_width, img_height = img.size
    scale = min(target_width / img_width, target_height / img_height)
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)

    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2

    canvas.paste(resized_img, (x_offset, y_offset))

    palette = Image.new("P", (1, 1))
    colors = 3
    
    # Apply appropriate color conversion
    if specs.second_color:
        palette.putpalette([
            0, 0, 0,  # Black
            255, 255, 255,  # White
            255, 0, 0  # Red
        ])
    else:
        palette.putpalette([
            0, 0, 0,  # Black
            255, 255, 255,  # White
        ])
        colors = 2

    processed_img = canvas.quantize(method=Image.MEDIANCUT,
                                        colors=colors,
                                        kmeans=0,
                                        palette=palette)
    processed_img = processed_img.convert("RGB")
    
    return processed_img

