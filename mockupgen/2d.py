from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFilter
import os
import numpy as np
import cv2
from enum import Enum
from detectdim import get_tshirt_dimensions

class DesignPosition(Enum):
    MIDDLE = 1
    TOP_LEFT = 2
    TOP_RIGHT = 3

def extract_fabric_texture(tshirt_image, sample_size=100):
    # Extract a square sample from the middle of the t-shirt
    width, height = tshirt_image.size
    sample_x = (width - sample_size) // 2
    sample_y = (height - sample_size) // 2
    texture_sample = tshirt_image.crop((sample_x, sample_y, sample_x + sample_size, sample_y + sample_size))
    
    # Convert to grayscale to focus on texture rather than color
    texture_sample = texture_sample.convert('L')
    
    # Enhance contrast to make the texture more pronounced
    enhancer = ImageEnhance.Contrast(texture_sample)
    texture_sample = enhancer.enhance(1.5)
    
    return texture_sample

def create_fabric_texture(size, color=(200, 200, 200)):
    texture = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(texture)
    
    for x in range(0, size[0], 2):
        for y in range(0, size[1], 2):
            if (x + y) % 4 == 0:
                draw.point((x, y), fill=(180, 180, 180))
    
    return texture.convert('RGBA')

def analyze_design(design):
    # Convert to grayscale for analysis
    gray = design.convert('L')
    
    # Find the bounding box of the non-transparent content
    bbox = gray.getbbox()
    
    if bbox:
        content_width = bbox[2] - bbox[0]
        content_height = bbox[3] - bbox[1]
        aspect_ratio = content_width / content_height
    else:
        # Fallback if no content is found
        aspect_ratio = design.width / design.height
    
    return aspect_ratio, bbox

def calculate_optimal_size(max_size, aspect_ratio):
    max_width, max_height = max_size
    
    if max_width / aspect_ratio <= max_height:
        # Width is the limiting factor
        return max_width, int(max_width / aspect_ratio)
    else:
        # Height is the limiting factor
        return int(max_height * aspect_ratio), max_height

def create_tshirt_mockup(design_path, tshirt_path, position=DesignPosition.MIDDLE, size_ratio=0.5):
    design = Image.open(design_path).convert("RGBA")
    tshirt = Image.open(tshirt_path).convert("RGBA")

    (tshirt_width, tshirt_height), corners, safe_area = get_tshirt_dimensions(tshirt_path)

    # Adjust safe_area to be relative to the t-shirt corners
    tshirt_left, tshirt_top = corners[0]
    safe_left, safe_top, safe_right, safe_bottom = safe_area
    safe_left -= tshirt_left
    safe_right -= tshirt_left
    safe_top -= tshirt_top
    safe_bottom -= tshirt_top

    design_aspect_ratio = design.width / design.height
    safe_width = safe_right - safe_left
    safe_height = safe_bottom - safe_top

    # Calculate initial design size based on the size_ratio parameter
    design_width = int(safe_width * size_ratio)
    design_height = int(design_width / design_aspect_ratio)

    # Ensure the design fits within the safe area
    if design_height > safe_height * size_ratio:
        design_height = int(safe_height * size_ratio)
        design_width = int(design_height * design_aspect_ratio)

    # Resize the design
    design = design.resize((design_width, design_height), Image.LANCZOS)

    # Calculate position based on the enum, ensuring the entire design stays within the safe area
    if position == DesignPosition.MIDDLE:
        pos_x = safe_left + (safe_width - design_width) // 2
        pos_y = safe_top + (safe_height - design_height) // 2
    elif position == DesignPosition.TOP_LEFT:
        pos_x = safe_left + int(safe_width * 0.05)  # 5% padding from left
        pos_y = safe_top + int(safe_height * 0.05)  # 5% padding from top
    elif position == DesignPosition.TOP_RIGHT:
        pos_x = safe_right - design_width - int(safe_width * 0.05)  # 5% padding from right
        pos_y = safe_top + int(safe_height * 0.05)  # 5% padding from top
    else:
        raise ValueError("Invalid position specified")

    # Ensure the design stays completely within the safe area
    pos_x = max(safe_left, min(pos_x, safe_right - design_width))
    pos_y = max(safe_top, min(pos_y, safe_bottom - design_height))

    # Create the mockup
    mockup = tshirt.copy()
    mockup.paste(design, (pos_x + tshirt_left, pos_y + tshirt_top), design)

    return mockup

# Usage example:
if __name__ == "__main__":
    design_path = "/Users/ryan/Desktop/ezproof/email_191a54041fb5f7a5_IMG_3599.jpg_output/email_191a54041fb5f7a5_IMG_3599.jpg_isnet-general-use_alpha.png"
    tshirt_path = "/Users/ryan/Desktop/ezproof/mockupgen/materials/redtshirt.jpg"
    
    # Generate mockup with design in the middle, 50% of max size (default)
    mockup_middle = create_tshirt_mockup(design_path, tshirt_path,size_ratio=1)
    
    # Generate mockup with design in the top left, 30% of max size
    mockup_top_left = create_tshirt_mockup(design_path, tshirt_path, DesignPosition.TOP_LEFT, size_ratio=.7)
    
    # Generate mockup with design in the top right, 30% of max size
    mockup_top_right = create_tshirt_mockup(design_path, tshirt_path, DesignPosition.TOP_RIGHT, size_ratio=.7)

    # Save the results
    mockup_middle.save("mockup_middle.png")
    mockup_top_left.save("mockup_top_left.png")
    mockup_top_right.save("mockup_top_right.png")
