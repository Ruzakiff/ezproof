def load_processing_config():
    return {
        'image/jpeg': 'process_image',
        'image/png': 'process_image',
        'image/jpg': 'process_image',
        # Add more image types as needed
    }
