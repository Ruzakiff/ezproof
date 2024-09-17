import os
from backgroundremover.bg import remove
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# Use an environment variable for the API key
API_KEY = os.environ.get('API_KEY', 'default_api_key')

def require_api_key(view_function):
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key')
        if provided_key and provided_key == API_KEY:
            return view_function(*args, **kwargs)
        else:
            return jsonify({'error': 'Invalid or missing API key'}), 403
    return decorated_function

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
        return None

@app.route('/remove-background', methods=['POST'])
@require_api_key
def api_remove_background():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        base_filename = os.path.splitext(filename)[0]
        unique_id = str(uuid.uuid4())
        base_filename = f"{base_filename}_{unique_id}"
        
        image_data = file.read()
        results = remove_background_from_data(image_data, base_filename)
        
        if results is None:
            return jsonify({'error': 'An error occurred during processing'}), 500
        
        return jsonify({'results': results}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)