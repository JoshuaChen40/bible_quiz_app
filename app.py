import os
import json
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# =====================================================
# 🧩 初始化設定
# =====================================================
st.set_page_config(page_title="腦光一閃", page_icon="✝️", layout="wide")
load_dotenv()

# =====================================================
# 💅 全局樣式
# =====================================================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 1.1rem !important;
    line-height: 1.5em !important;
    overflow-x: hidden;
}
h1, h2, h3, h4, h5 {
    font-weight: 800 !important;
    color: #222 !important;
    line-height: 1.3em !important;
}
p, span, div {
    font-size: 1rem !important;
}
button, [data-testid="stButton"] button {
    font-size: 1.05rem !important;
    padding: 0.3em 0.8em !important;
    border-radius: 8px !important;
}
.stAlert {
    font-size: 1rem !important;
}
.block-container {
    padding-top: 0.8em !important;
    padding-bottom: 0.8em !important;
    max-width: 100% !important;
}
section.main > div {
    max-width: 95% !important;
}
[data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
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
# 💓 Render 保持喚醒節點
# =====================================================
if st.query_params.get("ping") == "1":
    st.write("pong 💓")
    st.stop()

# =====================================================
# 📘 題庫載入（支援加密）
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
        # 嘗試讀取 questions.json
        if os.path.exists("questions.json"):
            with open("questions.json", "r", encoding="utf-8") as f:
                QUESTIONS = json.load(f)
        else:
            st.error("❌ 找不到 questions.json 或 questions.enc")
            st.stop()
            
        if not QUIZ_SECRET_KEY:
             st.warning("⚠️ 未偵測到加密金鑰，目前使用明文 questions.json。")
             
    except Exception as e:
        st.error(f"❌ 題庫載入失敗：{e}")
        st.stop()

# =====================================================
# 🧠 Session 狀態初始化
# =====================================================
defaults = {
    "page": "login",
    "authenticated": False,
    "current_q": None,
    "show_answer": False,
    "show_answer_dialog": False,
    "answered_questions": [],
    "confirm_clear": False,
    # ✅ 新增：文字縮放倍率，預設 1.25 倍
    "text_scale": 1.25, 
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# =====================================================
# ⚙️ 共用函式
# =====================================================
def goto(page_name: str):
    st.session_state["page"] = page_name
    st.rerun()

def goto_question(idx: int):
    st.session_state["current_q"] = idx
    st.session_state["show_answer"] = False
    goto("question")

# =====================================================
# 🔐 登入頁
# =====================================================
def page_login():
    st.title("✝️ 腦光一閃登入")

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

    st.title("📚 腦光一閃題目集合")

    # ---- 分組顯示 ----
    groups = {}
    for i, q in enumerate(QUESTIONS):
        groups.setdefault(q["q_group"], []).append((i, q))

    cols = st.columns(len(groups))

    for c_idx, (group, items) in enumerate(groups.items()):
        with cols[c_idx]:
            st.markdown(f"### 🟩 {group}")
            for idx, q in items:
                q_type = q.get("q_type", "q")

                # 判斷顏色
                if idx in st.session_state["answered_questions"]:
                    color = "#000000"
                    text_color = "#FFFFFF"
                elif q_type == "warm_up":
                    color = "#FFD8A8"
                    text_color = "#000000"
                else:
                    color = "#E2ECF9"
                    text_color = "#000000"

                st.markdown(
                    f"""
                    <div style="
                        background-color:{color};
                        color:{text_color};
                        border-radius:10px;
                        padding:0.3em 0.1em;
                        margin-bottom:0.4em;
                        text-align:center;">
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(f"題目 {idx + 1}", key=f"btn_{idx}", use_container_width=True):
                    goto_question(idx)

                st.markdown("</div>", unsafe_allow_html=True)

    # ✅ 新增：文字縮放拉桿
    st.divider()
    st.markdown("### 🔍 題目文字大小調整")
    st.session_state["text_scale"] = st.slider(
        "選擇題目頁面文字縮放倍率 (基礎 1.1rem)",
        min_value=1.0,
        max_value=2.5,
        value=st.session_state["text_scale"],
        step=0.1,
        format="%.1f 倍",
        help="此倍率應用於題目頁面，基於全局字體大小 1.1rem 進行縮放。"
    )

    # ---- 底部操作區 ----
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🚪 登出"):
            st.session_state["authenticated"] = False
            goto("login")

    with col2:
        if not st.session_state["confirm_clear"]:
            if st.button("🧹 移除作答紀錄"):
                st.session_state["confirm_clear"] = True
                st.rerun()
        else:
            st.warning("⚠️ 是否確定要移除所有作答紀錄？")
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                if st.button("✅ 是，清除紀錄"):
                    st.session_state["answered_questions"].clear()
                    components.html(
                        "<script>localStorage.removeItem('bible_quiz_progress');</script>",
                        height=0,
                    )
                    st.success("✅ 已清除作答紀錄！")
                    st.session_state["confirm_clear"] = False
                    st.rerun()
            with sub_col2:
                if st.button("❌ 否"):
                    st.session_state["confirm_clear"] = False
                    st.rerun()

    with col3:
        if st.button("🔍 檢查 LocalStorage"):
            components.html(
                """
                <script>
                const data = localStorage.getItem('bible_quiz_progress');
                alert('目前 LocalStorage 紀錄：\\n' + (data ? data : '（尚無資料）'));
                </script>
                """,
                height=0,
            )

# =====================================================
# 📖 題目頁
# =====================================================
def page_question():
    if not st.session_state["authenticated"]:
        goto("login")

    # 讀取縮放倍率
    scale = st.session_state["text_scale"] 
    
    # 設置基礎大小 (base_rem = 1.1rem，取自全局樣式)
    base_rem = 1.1 
    
    # 計算新的 rem 值
    new_font_size = base_rem * scale 
    new_button_size = base_rem * scale * 0.9 # 按鈕稍微小一點
    
    # 應用放大字體（題目頁）
    st.markdown(f"""
    <style>
    /* 調整字體大小，使用動態計算的 rem 值 */
    h1, h2, h3, h4, h5, p, span, div, li {{
        font-size: {new_font_size:.2f}rem !important;
        line-height: 1.5em !important;
    }}
    button, [data-testid="stButton"] button {{
        font-size: {new_button_size:.2f}rem !important; 
        padding: 0.4em 1em !important;
    }}
    .stAlert {{ font-size: {new_button_size:.2f}rem !important; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 📖 題目頁面")

    try:
        q_idx = st.session_state.get("current_q")
        if q_idx is None or q_idx >= len(QUESTIONS):
            raise ValueError("題目不存在")

        q = QUESTIONS[q_idx]
        st.markdown(f"#### 題目 {q_idx + 1}")
        st.write(q["question"])
        # st.write("---")

        # ✅ 修改處：支援 A, B, C, D 並加入檢查
        for opt in ["A", "B", "C", "D"]:
            if opt in q and q[opt]: # 確保 JSON 中有該選項
                st.write(f"**({opt})** {q[opt]}")

        if st.button("📜 解答"):
            st.session_state["show_answer_dialog"] = True
            st.rerun()

        if st.session_state["show_answer_dialog"]:
            st.info("❓ 是否要公布答案？")
            col1, col2, _ = st.columns([1, 1, 3])
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
            if q_idx not in st.session_state["answered_questions"]:
                st.session_state["answered_questions"].append(q_idx)
            # 同步進 LocalStorage
            components.html(
                f"<script>localStorage.setItem('bible_quiz_progress', '{json.dumps(st.session_state['answered_questions'])}');</script>",
                height=0,
            )

    except Exception as e:
        st.error(f"⚠️ 題目載入錯誤：{e}")
        st.info("請回首頁重新選擇題目。")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.button("🏠 回首頁", on_click=lambda: goto("home"))
    with col2:
        st.button("🚪 登出", on_click=lambda: goto("login"))

# =====================================================
# 🚦 頁面路由
# =====================================================
page = st.session_state["page"]
if page == "login":
    page_login()
elif page == "home":
    page_home()
elif page == "question":
    page_question()

# =====================================================
# 🧠 啟動時從 LocalStorage 嘗試載入進度
# =====================================================
components.html(
    """
    <script>
    const progress = localStorage.getItem('bible_quiz_progress');
    if (progress) {{
        const pycmd = "st.session_state.answered_questions = JSON.parse('" + progress + "')";
    }}
    </script>
    """,
    height=0,
)