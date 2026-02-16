from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from backend.models.db import db 
from backend.models.user import User

# Initialize Blueprint and LoginManager
auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    """Fetches user from Azure SQL for session management."""
    return db.session.get(User, int(user_id))

@auth_bp.route('/api/login', methods=['POST'])
def login():
    """Authenticates users and establishes a 'sticky' cloud session."""
    data = request.json
    # Modern select for cross-context compatibility
    user = db.session.execute(db.select(User).filter_by(email=data.get('email'))).scalar_one_or_none()
    
    if user and check_password_hash(user.password_hash, data.get('password')):
        # remember=True ensures the cookie persists for file uploads
        login_user(user, remember=True) 
        return jsonify({
            'success': True, 
            'user': {
                'email': user.email, 
                'full_name': user.full_name,
                'is_admin': getattr(user, 'is_admin', False)
            }
        })
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@auth_bp.route('/api/register', methods=['POST'])
def register():
    """Creates a new researcher account in the Azure SQL database."""
    data = request.json
    hashed_pw = generate_password_hash(data.get('password'))
    
    new_user = User(
        email=data.get('email'),
        password_hash=hashed_pw,
        full_name=data.get('full_name'),
        institution=data.get('institution')
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        # Automatically log in after successful registration
        login_user(new_user, remember=True)
        return jsonify({
            'success': True, 
            'user': {'email': new_user.email, 'full_name': new_user.full_name}
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Registration failed (Email might exist)'}), 409

@auth_bp.route('/api/current-user')
def get_current_user():
    """Verifies the current session state."""
    if current_user.is_authenticated:
        return jsonify({
            'success': True, 
            'user': {'email': current_user.email, 'full_name': current_user.full_name}
        })
    return jsonify({'success': False, 'error': 'Not logged in'})

@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Terminates the cloud session."""
    logout_user()
    return jsonify({'success': True})