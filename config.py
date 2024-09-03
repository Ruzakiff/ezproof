def load_processing_config():
    return {
        'image/jpeg': 'process_image',
        'image/png': 'process_image',
        'image/jpg': 'process_image',
        # Add more image types as needed
    }

def load_print_config():
    return {
        'print_dpi': 300,
        'desired_width_inch': 8.5,
        'desired_height_inch': 11,
        'bleed_inch': 0.125,
    }

