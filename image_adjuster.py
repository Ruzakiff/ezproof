from PIL import Image, ImageEnhance
from io import BytesIO

def adjust_image(image_data, analysis_results, desired_width_inch, desired_height_inch):
    img = Image.open(BytesIO(image_data))
    
    # Aspect ratio adjustment
    img = adjust_aspect_ratio(img, desired_width_inch, desired_height_inch)
    
    if "sharpness" in analysis_results and "Image appears blurry" in analysis_results["sharpness"]:
        img = sharpen_image(img)
    
    if "exposure" in analysis_results:
        if "underexposed" in analysis_results["exposure"].lower():
            img = brighten_image(img)
        elif "overexposed" in analysis_results["exposure"].lower():
            img = darken_image(img)
    
    if "resolution" in analysis_results:
        width, height = map(int, analysis_results["resolution"].split(":")[1].strip().split("x"))
        if width < 2000 or height < 2000:  # Example threshold
            img = upscale_image(img)
    
    # Add more adjustments based on other analysis results
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

def adjust_aspect_ratio(img, desired_width_inch, desired_height_inch):
    current_ratio = img.width / img.height
    desired_ratio = desired_width_inch / desired_height_inch

    if abs(current_ratio - desired_ratio) < 0.01:  # If ratios are close enough, no change needed
        return img

    if current_ratio > desired_ratio:
        # Image is too wide, need to crop width
        new_width = int(img.height * desired_ratio)
        left = (img.width - new_width) // 2
        return img.crop((left, 0, left + new_width, img.height))
    else:
        # Image is too tall, need to crop height
        new_height = int(img.width / desired_ratio)
        top = (img.height - new_height) // 2
        return img.crop((0, top, img.width, top + new_height))

def sharpen_image(img):
    enhancer = ImageEnhance.Sharpness(img)
    return enhancer.enhance(1.5)  # Increase sharpness by 50%

def brighten_image(img):
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(1.2)  # Increase brightness by 20%

def darken_image(img):
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(0.8)  # Decrease brightness by 20%

def upscale_image(img):
    width, height = img.size
    return img.resize((width*2, height*2), Image.LANCZOS)