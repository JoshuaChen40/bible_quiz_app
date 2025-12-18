非常棒的進展 🎯
你已經完成了安全設計（加密題庫 + 環境變數金鑰），
現在要在 **本地用 Docker** 啟動這個 Streamlit 專案來測試。
我幫你一步步整理出 **完整、乾淨又能 100% 模擬 Render 的做法** 👇

---

## 🧱 一、專案結構確認

```
bible_quiz_app/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── encrypt_quiz_file.py
├── questions.enc
├── keep_alive.py
├── .env               # 放登入帳密與金鑰
└── .gitignore
```

---

## ⚙️ 二、`.env`（本地執行環境設定）

請在專案根目錄建立 `.env`（不會被上傳到 GitHub）：

```bash
BIBLE_QUIZ_USER=FKBC#1026
BIBLE_QUIZ_PASS=ROM#1026
QUIZ_SECRET_KEY=<你用 encrypt_quiz_file.py 產生的金鑰>
```

---

## 🐳 三、Dockerfile（Render + 本地通用版）

請使用這份：

```dockerfile
# =====================================================
# 🐳 Streamlit 聖經大車拼 Dockerfile
# =====================================================
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝必要系統套件
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxrender1 libxext6 curl && \
    rm -rf /var/lib/apt/lists/*

# 複製套件清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式檔案
COPY . .

# 設定環境變數（Streamlit 運行設定）
ENV PYTHONUNBUFFERED=1
ENV PORT=8501

# 開放 Streamlit 預設 port
EXPOSE 8501

# 啟動命令
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 📦 四、requirements.txt（固定版本）

請確保這份完整：

```txt
streamlit==1.38.0
python-dotenv==1.0.1
cryptography==43.0.0
requests==2.32.3
schedule==1.2.1
altair==5.4.1
pandas==2.2.2
numpy==1.26.4
protobuf==4.25.3
watchdog==4.0.2
```

---

## 🧠 五、建立與執行 Docker 容器

### 第一次建置 image：

```bash
docker build -t bible-quiz-app .
```

> 這會建立一個名稱為 `bible-quiz-app` 的映像。

---

### 執行容器（載入 .env 變數）：

```bash
docker run -p 8501:8501 --env-file .env bible-quiz-app
```

**說明：**

* `-p 8501:8501` → 將容器內的 Streamlit port 映射到本機 8501
* `--env-file .env` → 匯入登入帳密與金鑰

執行後，終端機會顯示：

```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

👉 開啟瀏覽器輸入：

```
http://localhost:8501
```

即可登入並測試整個系統 🎉

---

## 🧪 六、測試驗證流程

| 測試項目       | 驗證方式                                               |
| ---------- | -------------------------------------------------- |
| 登入功能       | 使用 `.env` 中的帳密登入                                   |
| 題庫解密       | 成功顯示題目列表代表金鑰與 `questions.enc` 解密成功                 |
| 題目頁        | 點任一題，顯示題幹與選項                                       |
| 解答         | 點「📜 解答」→ 彈窗 → 顯示答案                                |
| `/ping` 節點 | 在瀏覽器開 `http://localhost:8501/?ping=1`，應看到「pong 💓」 |

---

## 🔁 七、更新題庫流程（Docker 模式）

若你修改或新增題目：

1️⃣ 編輯 `questions.json`
2️⃣ 執行：

```bash
python3 encrypt_quiz_file.py
```

→ 生成新的 `questions.enc`
3️⃣ 重新 build：

```bash
docker build -t bible-quiz-app .
```

4️⃣ 再次執行：

```bash
docker run -p 8501:8501 --env-file .env bible-quiz-app
```

---

## ⚡ 八、快速本地啟動指令（整合版）

如果你想每次快速執行（不重建 image）：

```bash
docker stop bible-quiz || true && docker rm bible-quiz || true
docker run -d --name bible-quiz -p 8501:8501 --env-file .env bible-quiz-app
```

> * `-d` 讓容器在背景執行
> * 可以用 `docker logs -f bible-quiz` 查看執行紀錄

---

## ✅ 九、完成檢查表

| 項目                    | 狀態 |
| --------------------- | -- |
| Dockerfile 設定正確       | ✅  |
| requirements.txt 固定版本 | ✅  |
| .env 設好帳密與金鑰          | ✅  |
| questions.enc 存在      | ✅  |
| docker run 可啟動並登入     | ✅  |
| ping 節點可回應            | ✅  |

---

是否要我幫你再補一個
👉 `run_local.sh`（一鍵 build + run + 打開瀏覽器）
讓你只要輸入 `sh run_local.sh` 就能啟動整個容器測試？

---
# 生成PPT
```
sudo apt update

sudo apt install python3-pip

python3 -m pip --version

python3 -m pip install python-pptx==1.0.2
```