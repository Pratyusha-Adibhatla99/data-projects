from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv
import os, sys, subprocess, re, time

# 1. Import the neutral db instance
from backend.models.db import db

def create_app():
    """Application Factory to prevent Circular Imports and RuntimeErrors"""
    app = Flask(__name__, static_folder='../frontend')
    load_dotenv()

    # --- CONFIGURATION ---
    app.config['SECRET_KEY'] = 'dev-secret-key' 
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 * 1024 # 50GB Limit
    
    # Database Logic: Azure vs Local
    azure_db = os.getenv('DB_CONNECTION_STRING')
    if azure_db:
        app.config['SQLALCHEMY_DATABASE_URI'] = azure_db
        print("✅ CONNECTED TO AZURE SQL")
    else:
        PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        local_db_path = os.path.join(PROJECT_ROOT, 'database', 'wireless_data.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{local_db_path}'
        print("⚠️  USING LOCAL SQLITE")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- SESSION SECURITY FIXES (The "Sticky Session" Logic) ---
    # Inside create_app() in backend/app.py
    app.config.update(
    SESSION_COOKIE_NAME='wireless_cloud_session',
    SESSION_COOKIE_SAMESITE='Lax', # Critical for localhost navigation
    SESSION_COOKIE_SECURE=False,   # Must be False for http (non-https)
    SESSION_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_HTTPONLY=True
)

# Robust CORS to handle pre-flight OPTIONS requests
    CORS(app, 
     supports_credentials=True, 
     origins=["http://localhost:5001", "http://127.0.0.1:5001", "https://0.0.0.1:5001"],
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
     methods=["GET", "POST", "OPTIONS"])
    db.init_app(app)

    # --- CORS FIX ---
    # Moved inside create_app to ensure credentials (cookies) are permitted
    # Replace the existing CORS line with this:
    

    # 3. Register Blueprints and Handlers within App Context
    with app.app_context():
        from backend.routes.auth import auth_bp, login_manager
        
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        
        # API-Friendly Unauthorized Handler (Prevents browser confusion)
        @login_manager.unauthorized_handler
        def unauthorized():
            return jsonify({'success': False, 'error': 'Unauthorized. Please log in.'}), 401

        app.register_blueprint(auth_bp)

    return app

# Instantiate the app
app = create_app()

# --- SERVICES & GLOBAL VARS ---
_nb_proc = None
_nb_token = None

# Initialize BronzeService after app creation
from backend.services.bronze_service import BronzeService
from backend.processors.mat_processor import WirelessDataProcessor
from backend.processors.csv_processor import CSVProcessor

# Use the same DB source for the service layer
DATABASE_SOURCE = os.getenv('DB_CONNECTION_STRING')
UPLOAD_ROOT = os.path.join(os.path.dirname(__file__), '../uploads')
bronze_service = BronzeService(DATABASE_SOURCE, UPLOAD_ROOT)

# ─── ROUTES ───

@app.route('/')
def index():
    return send_file(os.path.join(app.static_folder, 'index.html'))

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
def get_my_files():
    try:
        # 1. Fetch from the database
        files = bronze_service.get_user_files(current_user.id)
        
        # 2. Fix the Datetime Serialization Crash
        for f in files:
            # Convert datetime objects to strings so JSON can read them
            if 'upload_time_pst' in f and f['upload_time_pst']:
                f['upload_time_pst'] = str(f['upload_time_pst'])
                
        # 3. Send safely to frontend
        return jsonify({'success': True, 'files': files})
        
    except Exception as e:
        print(f"Error fetching files: {e}")
        # Always return a valid 'files' array, even on error, to prevent frontend crashes
        return jsonify({'success': False, 'error': str(e), 'files': []})

# ... (rest of your routes)
# --- IMPORTS FOR ANALYSIS ---
from backend.processors.pcd_processor import PCDProcessor
# Assuming you have a mat_processor.py for .mat files
# from backend.processors.mat_processor import WirelessDataProcessor 
import tempfile

from flask import request, jsonify

# Notice we removed <filename> from the route path!
@app.route('/api/analyze', methods=['GET']) 
@login_required
def analyze_dataset():
    """
    Catches the Azure path from the frontend and routes it to the correct processor.
    The processor classes now handle their own downloading, analyzing, and cleanup.
    """
    try:
        # 1. Catch the exact Azure Blob Path sent by the frontend
        blob_path = request.args.get('path')
        
        if not blob_path:
            return jsonify({'success': False, 'error': 'No file path provided'})

        # Extract the extension (e.g., 'csv', 'mat', 'pcd')
        ext = blob_path.rsplit('.', 1)[-1].lower()
        metadata = {}

        # 2. Route to the correct processor
        # Pass the Azure blob_path directly to the processor classes
        if ext == 'csv':
            from backend.processors.csv_processor import CSVProcessor
            proc = CSVProcessor(blob_path)
            metadata = proc.get_metadata()
            
        elif ext == 'mat':
            from backend.processors.mat_processor import WirelessDataProcessor
            proc = WirelessDataProcessor(blob_path)
            metadata = proc.get_metadata()
            
        elif ext == 'pcd':
            from backend.processors.pcd_processor import PCDProcessor
            proc = PCDProcessor(blob_path)
            metadata = proc.get_metadata() 
            
        else:
            return jsonify({"success": False, "error": f"Analysis not supported for .{ext} files"})

        # 3. Check for processor-level errors (like h5py missing)
        if metadata.get('success') is False or 'error' in metadata:
            error_msg = metadata.get('error', 'Unknown analysis error')
            return jsonify({'success': False, 'error': error_msg})

        # 4. Return the glorious metadata to the React frontend
        return jsonify({'success': True, 'metadata': metadata})

    except Exception as e:
        print(f"Analysis Route Error: {e}")
        return jsonify({'success': False, 'error': str(e)})
    
if __name__ == '__main__':
    print("🚀 Wireless Platform (Cloud-Ready) Running on http://0.0.0.0:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
   