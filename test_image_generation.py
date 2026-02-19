"""
Test script for image generation endpoint
"""
import requests

BASE_URL = "https://omegaraisen-production.up.railway.app/api/v1"

def test_image_generation():
    """Test the image generation endpoint"""

    # Using the test account from user's data
    account_id = "cb1dfe0a-43a2-4e9b-9099-df6035f76700"
    prompt = "a beautiful sunset over mountains"
    style = "realistic"

    url = f"{BASE_URL}/content-lab/generate-image/"

    print(f"Testing image generation...")
    print(f"URL: {url}")
    print(f"Params: account_id={account_id}, prompt={prompt}, style={style}")
    print()

    try:
        # Send POST request with query params
        response = requests.post(
            url,
            params={
                "account_id": account_id,
                "prompt": prompt,
                "style": style
            },
            timeout=60
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()

        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS! ✅")
            print(f"Image URL: {data.get('image_url')}")
            print(f"Metadata: {data.get('metadata')}")
        else:
            print(f"ERROR ❌")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_image_generation()
