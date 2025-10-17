import os
import json
import streamlit as st
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# =====================================================
# 🧩 初始化設定
# =====================================================
st.set_page_config(page_title="聖經大車拼", page_icon="✝️", layout="wide")

# 讀取 .env（本地開發用）
load_dotenv()

# =====================================================
# 💅 全局樣式調整（投影幕專用字體放大）
# =====================================================
st.markdown("""
<style>
/* 整體文字放大 */
html, body, [class*="css"] {
    font-size: 2.5vw !important;  /* 約等於46pt */
    line-height: 1.4em !important;
}

/* 標題更醒目 */
h1, h2, h3, h4, h5 {
    font-weight: 800 !important;
    color: #222 !important;
}

/* 題目選項與說明 */
p, span, div {
    font-size: 2.3vw !important;
}

/* 按鈕放大 */
button, [data-testid="stButton"] button {
    font-size: 2.5vw !important;
    padding: 0.6em 1.4em !important;
    border-radius: 12px !important;
}

/* 成功與提示區塊 */
.stAlert {
    font-size: 2.3vw !important;
}

/* 調整區塊間距 */
.block-container {
    padding-top: 2em;
    padding-bottom: 2em;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 🔐 登入帳密與金鑰設定
# =====================================================
APP_USER = os.environ.get("BIBLE_QUIZ_USER", "")
APP_PASS = os.environ.get("BIBLE_QUIZ_PASS", "")
QUIZ_SECRET_KEY = os.environ.get("QUIZ_SECRET_KEY")

# =====================================================
# 💓 PING 節點：Render 保持喚醒用
# =====================================================
if st.query_params.get("ping") == "1":
    st.write("pong 💓")
    st.stop()

# =====================================================
# 📘 題庫載入：從加密檔案 questions.enc 解密
# =====================================================
QUESTIONS = None

if QUIZ_SECRET_KEY and os.path.exists("questions.enc"):
    try:
        fernet = Fernet(QUIZ_SECRET_KEY.encode())
        with open("questions.enc", "rb") as f:
            encrypted_data = f.read()
        decrypted = fernet.decrypt(encrypted_data)
        QUESTIONS = json.loads(decrypted.decode())
    except Exception as e:
        st.error(f"❌ 題庫解密失敗：{e}")
        st.stop()
else:
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            QUESTIONS = json.load(f)
        st.warning("⚠️ 未偵測到金鑰或加密檔，已使用本地 questions.json。")
    except Exception as e:
        st.error(f"❌ 題庫載入失敗：{e}")
        st.stop()

# =====================================================
# 🧠 初始化 Session State
# =====================================================
defaults = {
    "page": "login",
    "authenticated": False,
    "current_q": None,
    "show_answer": False,
    "show_answer_dialog": False
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# =====================================================
# ⚙️ 共用函式
# =====================================================
def goto(page_name: str):
    st.session_state["page"] = page_name
    st.rerun()

# =====================================================
# 🔐 登入頁面
# =====================================================
def page_login():
    st.title("✝️ 聖經大車拼登入")

    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")

    if st.button("登入"):
        if username == APP_USER and password == APP_PASS:
            st.session_state["authenticated"] = True
            goto("home")
        else:
            st.error("帳號或密碼錯誤")

# =====================================================
# 📚 題目集合頁
# =====================================================
def page_home():
    if not st.session_state["authenticated"]:
        goto("login")

    st.title("📚 聖經大車拼題目集合")

    groups = {}
    for i, q in enumerate(QUESTIONS):
        groups.setdefault(q["q_group"], []).append((i, q))

    for group, items in groups.items():
        st.markdown(f"### 🟩 {group}")
        cols = st.columns(len(items))
        for i, (idx, q) in enumerate(items):
            with cols[i]:
                if st.button(f"題目 {idx + 1}", key=f"btn_{idx}"):
                    st.session_state["current_q"] = idx
                    st.session_state["show_answer"] = False
                    goto("question")

    st.divider()
    if st.button("🚪 登出"):
        st.session_state["authenticated"] = False
        goto("login")

# =====================================================
# 📖 題目頁（容錯 + 大字體）
# =====================================================
def page_question():
    if not st.session_state["authenticated"]:
        goto("login")

    st.markdown("### 📖 題目頁面")

    error_happened = False
    q_idx = st.session_state.get("current_q")

    try:
        if q_idx is None or q_idx >= len(QUESTIONS):
            raise ValueError("題目編號不存在或超出範圍")

        q = QUESTIONS[q_idx]
        st.markdown(f"#### 題目 {q_idx + 1}")
        st.write(q["question"])
        st.write("---")

        for opt in ["A", "B", "C"]:
            st.write(f"**({opt})** {q[opt]}")

        if st.button("📜 解答"):
            st.session_state["show_answer_dialog"] = True
            st.rerun()

        if st.session_state["show_answer_dialog"]:
            st.info("❓ 是否要公布答案？")
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                if st.button("✅ 是"):
                    st.session_state["show_answer"] = True
                    st.session_state["show_answer_dialog"] = False
                    st.rerun()
            with col2:
                if st.button("❌ 否"):
                    st.session_state["show_answer_dialog"] = False
                    st.rerun()

        if st.session_state["show_answer"]:
            st.success(f"✅ 正確答案：{q['answer']}")
            st.info(f"💡 解釋：{q['explanation']}")

    except Exception as e:
        error_happened = True
        st.error(f"⚠️ 題目載入錯誤：{e}")
        st.info("請回首頁重新選擇題目。")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.button("🏠 回首頁", on_click=lambda: goto("home"))
    with col2:
        st.button("🚪 登出", on_click=lambda: goto("login"))

    if error_happened:
        st.warning("系統已忽略錯誤並保留操作功能。")

# =====================================================
# 🚦 Page Dispatcher
# =====================================================
page = st.session_state["page"]
if page == "login":
    page_login()
elif page == "home":
    page_home()
elif page == "question":
    page_question()
