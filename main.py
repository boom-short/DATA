Import json
import os
import time
from curl_cffi import requests
from datetime import datetime

# ফোল্ডার তৈরি
os.makedirs('data', exist_ok=True)

def fetch_and_save():
    api_key = "YOUR_SCRAPERANT_API_KEY" # ScraperAnt থেকে পাওয়া Key এখানে দিন
    target_url = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
    db_path = "data/wing_history.json"

    while True:
        try:
            print(f"[{datetime.now()}] Fetching data...")
            
            # ScraperAnt Proxy ব্যবহার করে Cloudflare বাইপাস
            proxy_url = f"https://api.scraperant.com/v2/general?url={target_url}&x-api-key={api_key}&browser=false"
            
            # ৩০ সেকেন্ডের গেমের জন্য ১০টি ডাটা আনা যথেষ্ট
            payload = {"pageIndex": 1, "pageSize": 10, "type": 30}
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(proxy_url, json=payload, headers=headers, timeout=60)

            if response.status_code == 200:
                data = response.json().get('data', {}).get('list', [])
                if data:
                    save_to_json(data, db_path)
                    print("✅ Data Updated Successfully.")
                else:
                    print("⚠️ No new data found in response.")
            else:
                print(f"❌ Error: {response.status_code}")

        except Exception as e:
            print(f"⚠️ System Error: {e}")

        # ৩০ সেকেন্ডের বিরতি (লুপ চলতে থাকবে)
        time.sleep(30)

def save_to_json(new_items, path):
    history = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try: history = json.load(f)
            except: history = []
    
    # ডুপ্লিকেট বাদ দিয়ে নতুন ডাটা যোগ
    existing_ids = {str(i['issueNumber']) for i in history}
    for item in new_items:
        if str(item['issueNumber']) not in existing_ids:
            history.append(item)
    
    # ডাটা সর্ট করে সেভ করা (সর্বশেষ ৫০০০ ডাটা রাখবে)
    history = sorted(history, key=lambda x: str(x['issueNumber']), reverse=True)[:5000]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    fetch_and_save()
