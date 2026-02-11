from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password_hash, full_name, institution=None):
        self.id = str(id)
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.institution = institution

    @property
    def is_admin(self):
        # HARDCODED ADMIN RULE: Only this specific email is Admin
        return self.email.lower() == 'dineshb@ucsd.edu'

    def get_id(self):
        return self.id
        
    def __repr__(self):
        return f'<User {self.email} (Admin: {self.is_admin})>'
