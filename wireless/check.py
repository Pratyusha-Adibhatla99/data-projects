
from backend.app import app
from backend.models.db import db
from sqlalchemy import text

with app.app_context():
    # Let's peek into the database and see EXACTLY what is there
    result = db.session.execute(text("SELECT id, filename, user_id, is_deleted FROM bronze_files")).fetchall()
    
    print(f"\n📊 TOTAL FILES FOUND IN AZURE SQL: {len(result)}")
    print("-" * 50)
    
    for row in result:
        print(f"File ID: {row[0]} | Name: {row[1]} | Owner (User ID): {row[2]} | Deleted Flag: {row[3]}")
        
    # Let's also check Aditya's actual User ID
    user = db.session.execute(text("SELECT id, email FROM [user] WHERE email LIKE '%aditya%'")).fetchone()
    if user:
        print("\n👤 ADITYA'S ACTUAL USER ID IS:", user[0])