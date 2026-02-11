from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
import sqlite3
import os
import sys

# Import User Model
try:
    from backend.models.user import User
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from backend.models.user import User

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

def get_db_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    project_root = os.path.abspath(os.path.join(base_dir, '../../')) 
    db_path = os.path.join(project_root, 'database', 'wireless_data.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@login_manager.user_loader
def load_user(user_id):
    try:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user is None: return None
        return User(user['id'], user['email'], user['password_hash'], user['full_name'], user['institution'])
    except: return None

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        user_obj = User(user['id'], user['email'], user['password_hash'], user['full_name'], user['institution'])
        login_user(user_obj)
        # INCLUDE is_admin IN RESPONSE
        return jsonify({
            'success': True, 
            'user': {
                'email': user['email'], 
                'full_name': user['full_name'],
                'is_admin': user_obj.is_admin # <--- Added
            }
        })
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    institution = data.get('institution')
    hashed_pw = generate_password_hash(password)
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (email, password_hash, full_name, institution) VALUES (?, ?, ?, ?)',
                     (email, hashed_pw, full_name, institution))
        conn.commit()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        user_obj = User(user['id'], user['email'], user['password_hash'], user['full_name'], user['institution'])
        login_user(user_obj)
        conn.close()
        return jsonify({
            'success': True, 
            'user': {
                'email': email, 
                'full_name': full_name,
                'is_admin': user_obj.is_admin # <--- Added
            }
        })
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'error': 'Email already exists'}), 409

@auth_bp.route('/api/current-user')
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({
            'success': True, 
            'user': {
                'email': current_user.email, 
                'full_name': current_user.full_name,
                'is_admin': current_user.is_admin # <--- Added
            }
        })
    return jsonify({'success': False, 'error': 'Not logged in'})

@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})
