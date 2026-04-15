# scripts/test_r2.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.r2_storage import upload_audio, download_audio, delete_audio

def test_r2():
    print("Testing R2 connection...")

    # 1. Upload a small test file
    test_bytes = b"speaksmart r2 test audio bytes"
    test_key = "test/r2_connection_test.txt"

    url = upload_audio(test_bytes, test_key, content_type="text/plain")
    print(f"✅ Upload successful: {url}")

    # 2. Download it back
    downloaded = download_audio(test_key)
    assert downloaded == test_bytes, "Downloaded bytes do not match uploaded bytes"
    print("✅ Download successful — bytes match")

    # 3. Delete the test file
    delete_audio(test_key)
    print("✅ Delete successful")

    print("\n✅ R2 is fully working.")

if __name__ == "__main__":
    test_r2()