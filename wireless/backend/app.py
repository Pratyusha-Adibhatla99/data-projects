from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_login import login_required, current_user
from backend.services.bronze_service import BronzeService
import subprocess, re, time, threading
import os, sys
from backend.routes.auth import auth_bp, login_manager
from backend.processors.mat_processor import WirelessDataProcessor
from backend.processors.csv_processor import CSVProcessor
# Add project root to path so we can import processors if needed later
sys.path.insert(0, os.path.dirname(__file__))
# Note: You can keep csv_processor.py and mat_processor.py where they are for now

app = Flask(__name__, static_folder='../frontend')
# Global variables for Jupyter
_nb_proc = None
_nb_token = None
app.config['SECRET_KEY'] = 'dev-secret-key' 
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 * 1024 # 50GB Limit

# Initialize Auth
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
app.register_blueprint(auth_bp)
CORS(app, supports_credentials=True)

# ─── CONFIG & SERVICE INIT ───
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UPLOAD_ROOT  = os.path.join(PROJECT_ROOT, 'uploads')
DATABASE     = os.path.join(PROJECT_ROOT, 'database', 'wireless_data.db')

# Initialize the Service Layer
bronze_service = BronzeService(DATABASE, UPLOAD_ROOT)

@app.route('/')
def index():
    return send_file(os.path.join(app.static_folder, 'index.html'))

# ─── ROUTES ───

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    
    files = request.files.getlist('file')
    dataset_name = request.form.get('dataset_name', 'Default_Dataset')
    
    success_count = 0
    errors = []

    for file in files:
        if file.filename == '': continue
        try:
            # Delegate logic to Service
            success, msg = bronze_service.process_upload(
                file, dataset_name, current_user.email, current_user.id, current_user.full_name
            )
            if success: success_count += 1
        except Exception as e:
            print(f"Error uploading {file.filename}: {e}")
            errors.append(str(e))
            
    return jsonify({
        'success': True, 
        'message': f'Processed {success_count} files.',
        'errors': errors
    })

@app.route('/api/files', methods=['GET'])
@login_required
def list_my_files():
    try:
        # Delegate logic to Service
        raw_files = bronze_service.get_user_files(current_user.id)
        
        # Format for Frontend
        files = []
        for f in raw_files:
            files.append({
                'name': f['filename'],
                'dataset': f['dataset_name'],
                'size': f['file_size'],
                'type': f['modality'],
                'extension': f['file_extension'],
                'upload_time': f['upload_time_pst'],
                'can_delete': True
            })
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# NOTE: Analyze route stays here for now as it uses Processors
# In Day 4, we can move this to 'analytics_service.py'
@app.route('/api/analyze/<filename>', methods=['GET'])
@login_required
def analyze_file(filename):
    try:
        # 1. Use Service to find the file path
        # (We can use a quick SQL query here or add a helper to the service)
        conn = bronze_service.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT file_path, file_extension FROM bronze_files WHERE user_id=? AND filename=?", 
                       (current_user.id, filename))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'success': False, 'error': 'File not found'}), 404
            
        filepath = row['file_path']
        ext = row['file_extension']
        
        # 2. Use the Processors we imported at the top
        metadata = {}
        if ext == 'mat':
            p = WirelessDataProcessor(filepath)
            data = p.read_file()
            # Convert numpy shapes to safe strings for JSON
            safe_vars = {k: {'shape': v.shape, 'dtype': str(v.dtype)} for k, v in data.items()}
            metadata = {'filename': filename, 'variables': safe_vars, 'file_type': 'MAT'}
        elif ext == 'csv':
            p = CSVProcessor(filepath)
            metadata = p.get_metadata()
            
        return jsonify({'success': True, 'metadata': metadata})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
# ─── JUPYTER ROUTES ───
@app.route('/api/notebook/launch', methods=['POST'])
def launch_notebook():
    global _nb_proc, _nb_token
    
    # 1. If already running, return the existing localhost URL
    if _nb_proc and _nb_proc.poll() is None:
        if _nb_token:
            return jsonify({
                'success': True, 
                'status': 'running', 
                'url': f'http://localhost:8888/?token={_nb_token}' # <--- FORCE LOCALHOST
            })
        
    try:
        # 2. Launch Jupyter (Bind to 0.0.0.0 so it works, but we won't send that IP to browser)
        cmd = [
            sys.executable, '-m', 'jupyter', 'notebook', 
            '--no-browser', 
            '--port=8888', 
            f'--notebook-dir={PROJECT_ROOT}', 
            '--ip=0.0.0.0', 
            '--allow-root'
        ]
        
        _nb_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # 3. Smart Token Reader (Wait up to 5 seconds)
        start_time = time.time()
        while time.time() - start_time < 5:
            line = _nb_proc.stdout.readline()
            if not line: break
            
            # Print to terminal so you can see it too
            print(f"[Jupyter] {line.strip()}")
            
            if 'token=' in line:
                m = re.search(r'token=([a-f0-9]+)', line)
                if m: 
                    _nb_token = m.group(1)
                    break
        
        if _nb_token:
            return jsonify({
                'success': True, 
                'status': 'started', 
                'url': f'http://localhost:8888/?token={_nb_token}' # <--- FORCE LOCALHOST
            })
        else:
            return jsonify({'success': False, 'error': 'Timed out waiting for Jupyter token'})

    except Exception as e:
        print(f"Jupyter Error: {e}")
        return jsonify({'success': False, 'error': str(e)})
if __name__ == '__main__':
    print("🚀 Wireless Platform (Modular) Running on http://0.0.0.0:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)