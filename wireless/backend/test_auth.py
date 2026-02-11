"""
Automated tests for authentication system
Run: python3 backend/test_auth.py
Make sure server is running first!
"""
import requests

BASE_URL = "http://localhost:5001"

def test_registration():
    """Test user registration"""
    print("\n=== Testing Registration ===")
    
    # Register new user
    response = requests.post(f"{BASE_URL}/api/register", json={
        "email": "aditya@ucsd.edu",
        "password": "aditya123",
        "full_name": "Aditya Sharma",
        "institution": "UCSD",
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    print("✅ Registration test passed")

def test_login():
    """Test user login"""
    print("\n=== Testing Login ===")
    
    # Create session to maintain cookies
    session = requests.Session()
    
    # Login
    response = session.post(f"{BASE_URL}/api/login", json={
        "email": "sayyal@ucsd.edu",
        "password": "ayyal123"
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    print("✅ Login test passed")
    
    # Check current user
    response = session.get(f"{BASE_URL}/api/current-user")
    print(f"\nCurrent user: {response.json()}")
    assert response.json()['user']['email'] == "sayyal@ucsd.edu"
    print("✅ Current user test passed")
    
    return session

def test_protected_route(session):
    """Test protected route access"""
    print("\n=== Testing Protected Route ===")
    
    # Should work with session
    response = session.get(f"{BASE_URL}/api/current-user")
    print(f"With session: {response.status_code}")
    assert response.status_code == 200
    print("✅ Protected route accessible with session")
    
    # Should fail without session
    response = requests.get(f"{BASE_URL}/api/current-user")
    print(f"Without session: {response.status_code}")
    assert response.status_code == 401
    print("✅ Protected route blocked without session")

def test_logout(session):
    """Test logout"""
    print("\n=== Testing Logout ===")
    
    response = session.post(f"{BASE_URL}/api/logout")
    print(f"Logout: {response.json()}")
    assert response.json()['success'] == True
    
    # Should fail after logout
    response = session.get(f"{BASE_URL}/api/current-user")
    assert response.status_code == 401
    print("✅ Logout test passed")

if __name__ == "__main__":
    print("=" * 60)
    print("AUTHENTICATION SYSTEM TESTS")
    print("=" * 60)
    print("\n⚠️  Make sure the server is running:")
    print("   python3 backend/app.py")
    print("\nPress Enter to continue...")
    input()
    
    try:
        test_registration()
        session = test_login()
        test_protected_route(session)
        test_logout(session)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print("   Make sure server is running: python3 backend/app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")