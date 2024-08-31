import os
import vtracer
from io import BytesIO

def convert_to_svg(input_path):
    try:
        base_filename = os.path.splitext(os.path.basename(input_path))[0]
        output_folder = f"{base_filename}_svg_output"
        os.makedirs(output_folder, exist_ok=True)

        # Define different conversion modes
        modes = [
            {"name": "default", "params": {}},
            {"name": "binary", "params": {"colormode": "binary"}},
            {"name": "detailed", "params": {
                "colormode": "color",
                "hierarchical": "stacked",
                "mode": "spline",
                "filter_speckle": 4,
                "color_precision": 6,
                "layer_difference": 16,
                "corner_threshold": 60,
                "length_threshold": 4.0,
                "max_iterations": 10,
                "splice_threshold": 45,
                "path_precision": 3
            }}
        ]

        results = []
        for mode in modes:
            try:
                output_path = os.path.join(output_folder, f"{base_filename}_{mode['name']}.svg")
                vtracer.convert_image_to_svg_py(input_path, output_path, **mode['params'])
                print(f"Image converted to SVG using {mode['name']} mode. Output saved to {output_path}")
                results.append({
                    'mode': mode['name'],
                    'filename': f"{base_filename}_{mode['name']}.svg",
                    'path': output_path
                })
            except Exception as mode_error:
                print(f"Error processing {mode['name']} mode: {str(mode_error)}")
                continue

        print(f"All SVG conversion operations completed. Results saved in {output_folder}")
        return results
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def convert_to_svg_from_data(data, base_filename):
    try:
        output_folder = f"{base_filename}_svg_output"
        os.makedirs(output_folder, exist_ok=True)

        # Define different conversion modes
        modes = [
            {"name": "default", "params": {}},
            {"name": "binary", "params": {"colormode": "binary"}},
            {"name": "detailed", "params": {
                "colormode": "color",
                "hierarchical": "stacked",
                "mode": "spline",
                "filter_speckle": 4,
                "color_precision": 6,
                "layer_difference": 16,
                "corner_threshold": 60,
                "length_threshold": 4.0,
                "max_iterations": 10,
                "splice_threshold": 45,
                "path_precision": 3
            }}
        ]

        results = []
        for mode in modes:
            try:
                svg_str = vtracer.convert_raw_image_to_svg(data, **mode['params'])
                output_path = os.path.join(output_folder, f"{base_filename}_{mode['name']}.svg")
                with open(output_path, 'w') as f:
                    f.write(svg_str)
                print(f"Image converted to SVG using {mode['name']} mode. Output saved to {output_path}")
                results.append({
                    'mode': mode['name'],
                    'filename': f"{base_filename}_{mode['name']}.svg",
                    'path': output_path
                })
            except Exception as mode_error:
                print(f"Error processing {mode['name']} mode: {str(mode_error)}")
                continue

        print(f"All SVG conversion operations completed. Results saved in {output_folder}")
        return results
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    input_image = "/Users/ryan/Desktop/ezproof/h_output/h_u2netp_alpha.png"  # Replace with your input image path
    convert_to_svg(input_image)

    # Example for converting from raw image data
    with open(input_image, "rb") as f:
        image_data = f.read()
    base_filename = os.path.splitext(os.path.basename(input_image))[0]
    convert_to_svg_from_data(image_data, base_filename)
