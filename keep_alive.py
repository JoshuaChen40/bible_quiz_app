import requests, time

RENDER_URL = "https://bible-quiz.onrender.com/?ping=1"

while True:
    try:
        r = requests.get(RENDER_URL, timeout=10)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] PING {r.status_code}")
    except Exception as e:
        print("Ping failed:", e)
    time.sleep(600)  # 每10分鐘
