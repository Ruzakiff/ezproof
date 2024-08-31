import cv2
import numpy as np
from PIL import Image

def detect_tshirt_dimensions(image_path):
    # Read the image
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    
    # Define standard t-shirt proportions
    tshirt_width_ratio = 0.8  # T-shirt width is about 80% of image width
    tshirt_height_ratio = 0.6  # T-shirt height is about 60% of image height
    
    # Calculate t-shirt dimensions
    tshirt_width = int(w * tshirt_width_ratio)
    tshirt_height = int(h * tshirt_height_ratio)
    
    # Calculate t-shirt position
    left = int((w - tshirt_width) / 2)
    top = int(h * 0.2)  # Assume t-shirt starts at 20% from the top
    right = left + tshirt_width
    bottom = top + tshirt_height
    
    # Define corners
    corners = np.array([[left, top], [right, top], [right, bottom], [left, bottom]])
    
    # Define more conservative safe area
    safe_left = int(left + tshirt_width * 0.25)
    safe_right = int(right - tshirt_width * 0.25)
    safe_top = int(top + tshirt_height * 0.3)
    safe_bottom = int(bottom - tshirt_height * 0.2)
    
    safe_area = (safe_left, safe_top, safe_right, safe_bottom)
    
    return (tshirt_width, tshirt_height), corners, safe_area

def get_tshirt_dimensions(image_path):
    with Image.open(image_path) as img:
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            temp_path = 'temp_rgb_image.jpg'
            rgb_img.save(temp_path)
            dimensions, corners, safe_area = detect_tshirt_dimensions(temp_path)
            import os
            os.remove(temp_path)
        else:
            dimensions, corners, safe_area = detect_tshirt_dimensions(image_path)
    
    return dimensions, corners, safe_area

def visualize_output_area(image_path, corners, safe_area):
    # Read the image
    img = cv2.imread(image_path)
    
    # Draw the t-shirt corners
    cv2.drawContours(img, [corners], 0, (0, 255, 0), 2)
    
    # Draw the safe area
    safe_left, safe_top, safe_right, safe_bottom = safe_area
    cv2.rectangle(img, (safe_left, safe_top), (safe_right, safe_bottom), (0, 0, 255), 2)
    
    # Add text
    cv2.putText(img, "Safe Area", (safe_left, safe_top - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    
    # Show the image
    cv2.imshow("T-shirt with Safe Area", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Usage example
if __name__ == "__main__":
    tshirt_path = "/Users/ryan/Desktop/ezproof/mockupgen/materials/rawred.jpg"
    (width, height), corners, safe_area = get_tshirt_dimensions(tshirt_path)
    print(f"Detected t-shirt dimensions: {width}x{height}")
    print(f"T-shirt corners: {corners}")
    print(f"Safe output area: {safe_area}")
    
    # Visualize the safe area
    visualize_output_area(tshirt_path, corners, safe_area)
