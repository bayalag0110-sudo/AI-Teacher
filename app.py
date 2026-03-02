import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2
import gspread
from google.oauth2.service_account import Credentials

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v4.1", layout="wide", page_icon="🎓")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .teacher-header { background: linear-gradient(90deg, #1e3a8a, #3b82f6); padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px; }
    .student-header { background: linear-gradient(90deg, #064e3b, #10b981); padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px; }
    .glass-card { background: white; border-radius: 15px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .main-title { text-align: center; font-weight: 800; background: linear-gradient(90deg, #2563eb, #9333ea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE SHEETS API & WORD FUNCTIONS ---
def get_gsheet_client():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds)
    except: return None

def save_plan_to_cloud(doc_type, topic, content):
    ps_id = st.session_state.get('personal_sheet_id', '')
    if not ps_id: return False
    try:
        client = get_gsheet_client()
        sheet = client.open_by_key(ps_id).sheet1
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        sheet.append_row([now, doc_type, topic, content])
        return True
    except: return False

def create_word_doc(content):
    doc = Document()
    doc.add_heading('EduPlan Pro - Боловсруулсан материал', 0)
    doc.add_paragraph(content)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- LOGIN LOGIC ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='margin-top:80px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1 class='main-title'>EduPlan Pro</h1>", unsafe_allow_html=True)
        u_role = st.selectbox("Та хэн бэ?", ["Багш", "Сурагч"])
        u_name = st.text_input("Нэр:")
        u_class = st.text_input("Анги / Бүлэг (Жишээ нь: 10А):").upper()
        u_pwd = st.text_input("Нууц үг:", type="password")
        if st.button("Нэвтрэх"):
            if u_pwd == "admin1234" and u_name and u_class:
                st.session_state.auth, st.session_state.role, st.session_state.user, st.session_state.u_class = True, u_role, u_name, u_class
                st.rerun()
            else: st.error("Мэдээлэл дутуу байна!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user}")
    st.caption(f"📍 {st.session_state.role} | 🏫 {st.session_state.u_class}")
    if st.session_state.role == "Багш":
        st.session_state.personal_sheet_id = st.text_input("Google Sheet ID (Хувийн)", value=st.session_state.get('personal_sheet_id', ''))
        menu = st.radio("ЦЭС", ["💎 Ээлжит төлөвлөгч", "📝 Даалгавар өгөх", "📥 Ирсэн даалгавар", "🤖 AI Чатбот", "📊 Миний сан", "🌍 Портал"])
    else:
        menu = st.radio("ЦЭС", ["📚 Миний даалгавар", "📤 Даалгавар илгээх", "🤖 AI Туслах"])
    if st.button("🚪 Гарах"): st.session_state.auth = False; st.rerun()

# --- БАГШИЙН ХЭСЭГ: ЭЭЛЖИТ ТӨЛӨВЛӨГӨӨ ---
if st.session_state.role == "Багш" and menu == "💎 Ээлжит төлөвлөгч":
    st.markdown("<div class='teacher-header'><h1>💎 Ээлжит хичээл төлөвлөлт</h1></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        p_file = st.file_uploader("Сурах бичиг (PDF)", type="pdf")
        p_start = st.number_input("Эхлэх хуудас", 1, value=1)
        p_end = st.number_input("Дуусах хуудас", 1, value=3)
        p_tpc = st.text_input("Сэдвийн нэр")
        if st.button("🚀 Боловсруулах"):
            if p_file and p_tpc:
                with st.spinner("AI текстийг шинжилж байна..."):
                    reader = PyPDF2.PdfReader(p_file)
                    p_text = "".join([reader.pages[i].extract_text() for i in range(p_start-1, min(p_end, len(reader.pages)))])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"Чи бол мэргэжлийн багш. Текст: {p_text[:5000]}. Сэдэв: {p_tpc}. 45 минутын хичээлийн төлөвлөгөө гарга."
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    if res.status_code == 200:
                        st.session_state.last_plan = res.json()['choices'][0]['message']['content']
                        save_plan_to_cloud("Төлөвлөгөө", p_tpc, st.session_state.last_plan)
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        if 'last_plan' in st.session_state:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(st.session_state.last_plan)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.last_plan), f"{p_tpc}_plan.docx")
            st.markdown("</div>", unsafe_allow_html=True)

# --- БАГШИЙН ХЭСЭГ: ДААЛГАВАР ӨГӨХ ---
elif st.session_state.role == "Багш" and menu == "📝 Даалгавар өгөх":
    st.markdown("<div class='teacher-header'><h1>📝 Даалгавар нийтлэх</h1></div>", unsafe_allow_html=True)
    with st.form("hw_form"):
        hw_title = st.text_input("Даалгаврын гарчиг")
        hw_desc = st.text_area("Зааварчилгаа (Сурагчдад харагдана)")
        hw_deadline = st.date_input("Дуусах хугацаа")
        if st.form_submit_button("🚀 Нийтлэх"):
            # Google Sheet рүү 'Даалгавар' төрлөөр хадгалах логик
            save_plan_to_cloud(f"Даалгавар ({st.session_state.u_class})", hw_title, hw_desc)
            st.success(f"✅ {st.session_state.u_class} ангийн сурагчдад даалгавар илгээгдлээ.")

# --- СУРАГЧИЙН ХЭСЭГ: МИНИЙ ДААЛГАВАР ---
elif st.session_state.role == "Сурагч" and menu == "📚 Миний даалгавар":
    st.markdown("<div class='student-header'><h1>📚 Миний даалгавар</h1></div>", unsafe_allow_html=True)
    # Энд Google Sheet-ээс 'Class' баганаар шүүж харуулна (Жишээ байдлаар харуулав)
    st.markdown(f"""
    <div class='glass-card'>
        <h3>📗 Шинэ даалгавар: {st.session_state.u_class} анги</h3>
        <p><b>Сэдэв:</b> Математик - Процент</p>
        <p><b>Заавар:</b> Сурах бичгийн 120-р хуудас, 5-10-р бодлогыг бодоорой.</p>
        <hr>
        <p style='color:red;'>⏰ Хугацаа: 2024-05-30 хүртэл</p>
    </div>
    """, unsafe_allow_html=True)

# --- AI ЧАТБОТ (Бүх хэрэглэгчид) ---
elif "AI" in menu:
    st.markdown("<h2 class='main-title'>🤖 EduPlan AI Туслах</h2>", unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if p := st.chat_input("Асуултаа бичнэ үү..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": st.session_state.messages})
        ans = res.json()['choices'][0]['message']['content']
        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

# --- МИНИЙ САН & ПОРТАЛ (Өмнөх логикоор) ---
elif menu == "📊 Миний сан":
    st.markdown("<h2 class='main-title'>📊 Хадгалсан материалууд</h2>", unsafe_allow_html=True)
    # Google Sheet унших хэсэг
elif menu == "🌍 Портал":
    t1, t2 = st.tabs(["📚 E-Content", "✅ Үнэлгээ"])
    with t1: components.iframe("https://econtent.edu.mn/book", height=700)
    with t2: components.iframe("https://unelgee.eec.mn/", height=700)
