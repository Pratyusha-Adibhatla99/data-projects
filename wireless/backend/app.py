import os
from datetime import datetime, timedelta, timezone
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from sqlalchemy import text
import sys
from sqlalchemy import text 
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv
import re, time, subprocess

# 1. Import the neutral db instance
from backend.models.db import db
print("🟢 APP DB ID:", id(db))
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
     origins=[
         "http://localhost:5173", 
         "http://127.0.0.1:5173", 
         "http://localhost:5001"
     ],
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
     methods=["GET", "POST", "OPTIONS"])
    db.init_app(app)
    

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
def get_files():
    try:
        # 1. Fetch YOUR personal upload history (Bronze & Silver)
        my_query = text("SELECT * FROM bronze_files WHERE user_id = :uid")
        my_result = db.session.execute(my_query, {"uid": current_user.id}).fetchall()
        
        my_files = []
        for row in my_result:
            my_files.append({
                'id': getattr(row, 'id', 0),
                'filename': getattr(row, 'filename', 'Unknown'),
                'file_path': getattr(row, 'file_path', ''),
                'file_size': getattr(row, 'file_size', 0),
                'raw_upload_time': str(row.raw_upload_time) if getattr(row, 'raw_upload_time', None) else None,
                'dataset_name': getattr(row, 'dataset_name', 'Default_Dataset'),
                'processing_status': getattr(row, 'processing_status', 'unprocessed'),
                'sensor_type': getattr(row, 'sensor_type', 'Uncategorized')
            })

        # 2. Fetch the LAB'S global processed data (Only Silver, from EVERYONE)
        lab_query = text("""
            SELECT f.*, u.full_name as uploader_name 
            FROM bronze_files f
            JOIN users u ON f.user_id = u.id
            WHERE f.processing_status = 'silver_processed'
        """)
        lab_result = db.session.execute(lab_query).fetchall()
        
        lab_files = []
        for row in lab_result:
            lab_files.append({
                'id': getattr(row, 'id', 0),
                'filename': getattr(row, 'filename', 'Unknown'),
                'file_path': getattr(row, 'file_path', ''),
                'file_size': getattr(row, 'file_size', 0),
                'raw_upload_time': str(row.raw_upload_time) if getattr(row, 'raw_upload_time', None) else None,
                'dataset_name': getattr(row, 'dataset_name', 'Default_Dataset'),
                'processing_status': getattr(row, 'processing_status', 'silver_processed'),
                'sensor_type': getattr(row, 'sensor_type', 'Uncategorized'),
                'uploader_name': getattr(row, 'uploader_name', 'Unknown User') # Tell React who uploaded it!
            })
            
        # Send both lists back to React
        return jsonify({'success': True, 'my_files': my_files, 'lab_files': lab_files})
        
    except Exception as e:
        print(f"❌ CRITICAL SQL ERROR in /api/files: {e}")
        return jsonify({'success': False, 'error': str(e), 'my_files': [], 'lab_files': []})
# --- IMPORTS FOR ANALYSIS ---
from backend.processors.pcd_processor import PCDProcessor
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
@app.route('/api/download', methods=['GET'])
@login_required
def generate_download_link():
    try:
        file_path = request.args.get('path')
        if not file_path:
            return jsonify({"success": False, "error": "No file path provided"}), 400

        # 1. 🚨 THE UCSD SECURITY GATE 🚨
        # current_user automatically holds the logged-in user's data!
        user_email = current_user.email.lower()
        if not user_email.endswith('@ucsd.edu'):
            return jsonify({
                "success": False, 
                "error": f"Access Denied. {user_email} is not an authorized @ucsd.edu researcher account."
            }), 403

        # 2. Log the download in Azure SQL using SQLAlchemy
        try:
            log_query = text("""
                INSERT INTO download_logs (user_id, file_path, download_time_utc) 
                VALUES (:uid, :path, GETUTCDATE())
            """)
            db.session.execute(log_query, {"uid": current_user.id, "path": file_path})
            db.session.commit()
            print(f"✅ LOG: UCSD User {user_email} downloaded {file_path}")
        except Exception as log_err:
            print(f"⚠️ Warning: Could not log download (did you create the table?): {log_err}")
            db.session.rollback() # Prevent the database from locking up

        # 3. Generate the 1-hour SAS Token for Azure
        account_name = os.getenv("AZURE_ACCOUNT_NAME") 
        account_key = os.getenv("AZURE_ACCOUNT_KEY")
        container_name = "bronze" # Make sure this matches your container!

        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=file_path,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=1) 
        )

        sas_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{file_path}?{sas_token}"

        return jsonify({"success": True, "download_url": sas_url})

    except Exception as e:
        print(f"❌ Download Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

from backend.models.user import User # Make sure User is imported!

@app.route('/api/users', methods=['GET'])
@login_required
def get_all_users():
    try:
        # Fetch all users from the Azure SQL database
        users = User.query.all()
        
        # Package them securely (never send passwords to the frontend!)
        user_list = [{
            'id': u.id,
            'full_name': u.full_name,
            'email': u.email,
            'institution': u.institution,
            'is_admin': getattr(u, 'is_admin', False) 
        } for u in users]
        
        return jsonify({'success': True, 'users': user_list})
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500  
if __name__ == '__main__':
    print("🚀 Wireless Platform (Cloud-Ready) Running on http://0.0.0.0:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
   