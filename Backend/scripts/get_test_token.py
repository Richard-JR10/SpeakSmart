# scripts/get_test_token.py
import httpx
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Replace these with a real test account you created in Firebase Console
TEST_EMAIL = "testuser@speaksmart.dev"
TEST_PASSWORD = "testpassword123"
FIREBASE_API_KEY = "AIzaSyBBJC-_jc_jUN8pen7v2aC9yTMgmsD4ajY"  # From Firebase Console → Project Settings → Web API Key

def get_token():
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    response = httpx.post(url, json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "returnSecureToken": True,
    })
    data = response.json()

    if "idToken" not in data:
        print(f"❌ Login failed: {data}")
        return

    print("\n✅ Firebase ID Token (copy this into Swagger Authorize):\n")
    print(data["idToken"])
    print(f"\n  Expires in: {data['expiresIn']} seconds")

if __name__ == "__main__":
    get_token()