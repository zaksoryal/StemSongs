import os
from flask import Flask, render_template, request, jsonify
from separate_stems import process_with_demucs
from stem_comparison import compare_stems
import numpy as np  # Add this import for numpy

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
STEMMED_FOLDER = os.path.join(UPLOAD_FOLDER, 'Stemmed_Uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to convert float32 to standard Python float
def convert_to_python_float(obj):
    if isinstance(obj, np.float32):
        return float(obj)  # Convert float32 to Python's native float
    elif isinstance(obj, dict):
        return {key: convert_to_python_float(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_python_float(item) for item in obj]
    return obj

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(STEMMED_FOLDER, exist_ok=True)

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    uploaded_stems_dir = process_with_demucs(filepath, STEMMED_FOLDER)

    downloaded_songs_dir = './downloaded_songs'
    similarity_results = compare_stems(uploaded_stems_dir, downloaded_songs_dir)

    # Convert similarity_results to ensure float32 values are serialized correctly
    similarity_results = convert_to_python_float(similarity_results)

    return jsonify({"message": "File uploaded, processed, and compared", "similarity_results": similarity_results}), 200

if __name__ == '__main__':
    app.run(debug=True)
