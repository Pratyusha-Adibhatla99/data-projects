from backend.app import app
from backend.models.db import db
from backend.models.user import User
from sqlalchemy import text

with app.app_context():
    # 1. Find Aditya safely using the ORM
    aditya = User.query.filter(User.email.like('%aditya%')).first()
    
    if aditya:
        print(f"👤 Found Aditya! His real User ID is: {aditya.id}")
        
        # 2. Transfer all 300 files to his ID
        sql = text(f"UPDATE bronze_files SET user_id = {aditya.id}")
        db.session.execute(sql)
        db.session.commit()
        
        print("✅ SUCCESS! All 300 files have been securely transferred to Aditya.")
    else:
        print("❌ Could not find Aditya in the database.")