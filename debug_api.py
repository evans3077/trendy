# debug_api.py
import requests
import json

def test_ai_api():
    print("🧪 Testing AI Scraper API Directly")
    
    url = "https://ai-web-scraper1.p.rapidapi.com/"
    payload = {
        "url": "https://www.jumia.co.ke/catalog/?q=laptop",
        "summary": False
    }
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": "ai-web-scraper1.p.rapidapi.com",
        "x-rapidapi-key": "babf0b9047msh249b64e68aba30bp161856jsn54acc2ed7be7"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Type: {type(response.json())}")
        
        data = response.json()
        print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        print(f"Sample Content: {str(data)[:500]}...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ai_api()