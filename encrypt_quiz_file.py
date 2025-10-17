# encrypt_quiz_file.py
from cryptography.fernet import Fernet
import json

# 1️⃣ 若沒有金鑰，先產生一次性金鑰
key = Fernet.generate_key()
print("🔑 Secret Key（請放到 Render 環境變數 QUIZ_SECRET_KEY）:\n", key.decode())

# 2️⃣ 讀取原始題庫
with open("questions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

plain_text = json.dumps(data, ensure_ascii=False)
fernet = Fernet(key)
encrypted = fernet.encrypt(plain_text.encode())

# 3️⃣ 寫出加密後檔案
with open("questions.enc", "wb") as f:
    f.write(encrypted)

print("\n✅ 已建立加密題庫檔案：questions.enc")
