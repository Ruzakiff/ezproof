import os
from backgroundremover.bg import remove
from io import BytesIO

def remove_background(input_path):
    try:
        model_choices = ["u2net", "u2netp", "u2net_human_seg", "silueta", "isnet-general-use", "sam"]
        with open(input_path, "rb") as f:
            data = f.read()
        
        base_filename = os.path.splitext(os.path.basename(input_path))[0]
        output_folder = f"{base_filename}_output"
        os.makedirs(output_folder, exist_ok=True)
        
        for model in model_choices:
            try:
                # Without alpha matting
                img = remove(data, model_name=model)
                with open(os.path.join(output_folder, f"{base_filename}_{model}.png"), "wb") as f:
                    f.write(img)
                print(f"Background removed using {model} without alpha matting. Output saved to {os.path.join(output_folder, f'{base_filename}_{model}.png')}")

                # With alpha matting
                img_alpha = remove(data, model_name=model,
                                   alpha_matting=True,
                                   alpha_matting_foreground_threshold=230,
                                   alpha_matting_background_threshold=20,
                                   alpha_matting_erode_structure_size=10)
                output_path_alpha = os.path.join(output_folder, f"{base_filename}_{model}_alpha.png")
                with open(output_path_alpha, "wb") as f:
                    f.write(img_alpha)
                print(f"Background removed using {model} with alpha matting. Output saved to {output_path_alpha}")
            except Exception as model_error:
                print(f"Error processing model {model}: {str(model_error)}")
                continue  # Skip to the next model if there's an error
        
        print(f"All background removal operations completed. Results saved in {output_folder}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def remove_background_from_data(data, base_filename):
    try:
        model_choices = ["u2net", "u2netp", "u2net_human_seg", "silueta", "isnet-general-use", "sam"]
        
        output_folder = f"{base_filename}_output"
        os.makedirs(output_folder, exist_ok=True)
        
        results = []
        for model in model_choices:
            try:
                # Process image for each model
                img = remove(data, model_name=model)
                with open(os.path.join(output_folder, f"{base_filename}_{model}.png"), "wb") as f:
                    f.write(img)
                print(f"Background removed using {model} without alpha matting. Output saved to {os.path.join(output_folder, f'{base_filename}_{model}.png')}")

                # With alpha matting
                img_alpha = remove(data, model_name=model,
                                   alpha_matting=True,
                                   alpha_matting_foreground_threshold=230,
                                   alpha_matting_background_threshold=20,
                                   alpha_matting_erode_structure_size=10)
                output_path_alpha = os.path.join(output_folder, f"{base_filename}_{model}_alpha.png")
                with open(output_path_alpha, "wb") as f:
                    f.write(img_alpha)
                print(f"Background removed using {model} with alpha matting. Output saved to {output_path_alpha}")

                results.append({
                    'model': model,
                    'without_alpha': {
                        'filename': f"{base_filename}_{model}.png",
                        'path': os.path.join(output_folder, f"{base_filename}_{model}.png")
                    },
                    'with_alpha': {
                        'filename': f"{base_filename}_{model}_alpha.png",
                        'path': os.path.join(output_folder, f"{base_filename}_{model}_alpha.png")
                    }
                })
            except Exception as model_error:
                print(f"Error processing model {model}: {str(model_error)}")
                continue  # Skip to the next model if there's an error
        
        return results
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    input_image = "/Users/ryan/Desktop/ezproof/for_honored_bigdoggydog.png"  # Replace with your input image path
    with open(input_image, "rb") as f:
        image_data = f.read()
    base_filename = os.path.splitext(os.path.basename(input_image))[0]
    remove_background_from_data(image_data, base_filename)
