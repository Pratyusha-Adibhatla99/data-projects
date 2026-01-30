from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(__file__))
from mat_processor import WirelessDataProcessor

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Increase max upload size to 500MB
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'channels_release')
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
ALLOWED_EXTENSIONS = {'mat'}

# Create upload directory
os.makedirs(UPLOAD_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/files')
def list_files():
    try:
        data_files = []
        upload_files = []
        
        if os.path.exists(DATA_DIR):
            data_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.mat')]
        
        if os.path.exists(UPLOAD_DIR):
            upload_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.mat')]
        
        file_list = []
        
        for fname in sorted(data_files):
            fpath = os.path.join(DATA_DIR, fname)
            file_list.append({
                'name': fname,
                'size': os.path.getsize(fpath),
                'type': 'channels' if 'channels' in fname else 'timestamps',
                'source': 'original'
            })
        
        for fname in sorted(upload_files):
            fpath = os.path.join(UPLOAD_DIR, fname)
            file_list.append({
                'name': fname,
                'size': os.path.getsize(fpath),
                'type': 'channels' if 'channels' in fname else 'timestamps',
                'source': 'uploaded'
            })
        
        return jsonify({'success': True, 'files': file_list, 'count': len(file_list)})
    except Exception as e:
        print(f"Error listing files: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stats')
def get_stats():
    try:
        data_files = []
        upload_files = []
        
        if os.path.exists(DATA_DIR):
            data_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.mat')]
        
        if os.path.exists(UPLOAD_DIR):
            upload_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.mat')]
        
        all_files = data_files + upload_files
        
        channels_count = len([f for f in all_files if 'channels' in f])
        timestamps_count = len([f for f in all_files if 'timestamps' in f])
        
        total_size = 0
        if data_files:
            total_size += sum(os.path.getsize(os.path.join(DATA_DIR, f)) for f in data_files)
        if upload_files:
            total_size += sum(os.path.getsize(os.path.join(UPLOAD_DIR, f)) for f in upload_files)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_files': len(all_files),
                'channels_files': channels_count,
                'timestamps_files': timestamps_count,
                'total_size_mb': total_size / (1024*1024),
                'uploaded_files': len(upload_files)
            }
        })
    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        print("Upload request received")
        print(f"Files in request: {request.files}")
        
        if 'file' not in request.files:
            print("No file in request")
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        print(f"File object: {file}")
        print(f"Filename: {file.filename}")
        
        if file.filename == '':
            print("Empty filename")
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            print(f"File type not allowed: {file.filename}")
            return jsonify({'success': False, 'error': 'Only .mat files are allowed'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        print(f"Saving to: {filepath}")
        file.save(filepath)
        
        file_size = os.path.getsize(filepath)
        print(f"File saved successfully. Size: {file_size} bytes")
        
        return jsonify({
            'success': True, 
            'message': 'File uploaded successfully',
            'filename': filename,
            'size': file_size
        })
    except Exception as e:
        print(f"Upload error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analyze/<filename>')
def analyze_file(filename):
    try:
        # Check both directories
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            filepath = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'})
        
        print(f"Analyzing: {filepath}")
        processor = WirelessDataProcessor(filepath)
        data = processor.read_file()
        
        metadata = {
            'filename': filename,
            'file_size': os.path.getsize(filepath),
            'variables': {}
        }
        
        for var_name, var_data in data.items():
            metadata['variables'][var_name] = {
                'shape': list(var_data.shape),
                'dtype': str(var_data.dtype),
                'size': int(var_data.size),
                'ndim': int(var_data.ndim)
            }
            
            if var_data.dtype.kind in ['i', 'f']:
                metadata['variables'][var_name]['min'] = float(var_data.min())
                metadata['variables'][var_name]['max'] = float(var_data.max())
                metadata['variables'][var_name]['mean'] = float(var_data.mean())
        
        return jsonify({'success': True, 'metadata': metadata})
    except Exception as e:
        print(f"Analysis error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Wireless Data Platform Starting...")
    print("="*60)
    print(f"📁 Data directory: {DATA_DIR}")
    print(f"📤 Upload directory: {UPLOAD_DIR}")
    print(f"🌐 Web interface: http://localhost:5001")
    print(f"📊 Max upload size: 500 MB")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5001)