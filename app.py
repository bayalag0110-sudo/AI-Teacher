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
import time

# 1. ХУУДАСНЫ ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro AI v3.0", layout="wide", page_icon="🎓")

# Одоогийн цаг хугацаа авах
now_time = datetime.datetime.now()
current_date = now_time.strftime("%Y-%m-%d")
current_clock = now_time.strftime("%H:%M:%S")

# --- CUSTOM CSS ---
if 'theme' not in st.session_state: st.session_state.theme = 'light'
curr_theme = {
    'light': {'bg': '#f1f5f9', 'card': 'white', 'text': '#1e293b', 'accent': '#3b82f6'},
    'dark': {'bg': '#0f172a', 'card': '#1e293b', 'text': '#f8fafc', 'accent': '#60a5fa'}
}
curr = curr_theme[st.session_state.theme]

st.markdown(f"""
    <style>
    .stApp {{ background-color: {curr['bg']}; color: {curr['text']}; font-family: 'Inter', sans-serif; }}
    .stat-card {{
        background: {curr['card']}; border-radius: 15px; padding: 20px;
        text-align: center; border-left: 5px solid {curr['accent']};
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    .glass-card {{
        background: {curr['card']}; border-radius: 20px; padding: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px;
    }}
    .main-title {{
        text-align: center; font-weight: 800; font-size: 2.5rem;
        background: linear-gradient(90deg, #2563eb, #9333ea);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE SHEETS FUNCTIONS ---
def get_gsheet_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

def save_to_cloud(doc_type, topic, content):
    ps_id = st.session_state.get('personal_sheet_id', '')
    if not ps_id: return False
    try:
        client = get_gsheet_client()
        sheet = client.open_by_key(ps_id).sheet1
        sheet.append_row([current_date + " " + current_clock, doc_type, topic, content])
        return True
    except: return False

# --- WORD DOCUMENT GENERATOR ---
def create_word_doc(content):
    doc = Document()
    doc.add_heading('EduPlan Pro AI - Боловсруулсан материал', 0)
    doc.add_paragraph(content)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- LOGIN LOGIC ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div style="margin-top:100px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("<h1 class='main-title'>EduPlan Pro</h1>", unsafe_allow_html=True)
        st.write(f"📅 Өнөөдөр: {current_date}")
        login_name = st.text_input("Багшийн нэр")
        login_pwd = st.text_input("Нууц үг", type="password")
        if st.button("Нэвтрэх"):
            if login_pwd == "admin1234" and login_name:
                st.session_state.authenticated = True
                st.session_state.teacher_name = login_name
                st.session_state.login_time = current_clock
                st.rerun()
            else: st.error("Мэдээллээ бүрэн оруулна уу!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.teacher_name}")
    st.caption(f"🕒 Нэвтэрсэн: {st.session_state.login_time}")
    st.session_state.personal_sheet_id = st.text_input("Google Sheet ID", value=st.session_state.get('personal_sheet_id', ''))
    if st.button("🌓 Горим солих"):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()
    st.divider()
    menu = st.radio("ЦЭС", ["📊 Хянах самбар", "🤖 AI Чатбот", "💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📊 Миний сан", "🌍 Портал"])
    if st.button("🚪 Гарах"):
        st.session_state.authenticated = False
        st.rerun()

# --- 1. ХЯНАХ САМБАР (DASHBOARD) ---
if menu == "📊 Хянах самбар":
    st.markdown(f"<h1 class='main-title'>Сайн байна уу, {st.session_state.teacher_name} багшаа!</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>Өнөөдөр: {current_date} | Цаг: {current_clock}</p>", unsafe_allow_html=True)
    
    # Статистик авах
    total_docs = 0
    if st.session_state.personal_sheet_id:
        try:
            client = get_gsheet_client()
            data = client.open_by_key(st.session_state.personal_sheet_id).sheet1.get_all_records()
            total_docs = len(data)
        except: total_docs = "Холболтгүй"

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="stat-card"><h3>Нийт материал</h3><h1>{total_docs}</h1></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-card"><h3>Системийн төлөв</h3><h1 style="color:green;">Online</h1></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="stat-card"><h3>AI Модель</h3><p>Llama 3.3 70B</p></div>', unsafe_allow_html=True)

    

# --- 2. ЭЭЛЖИТ ТӨЛӨВЛӨГӨӨ ---
elif menu == "💎 Ээлжит төлөвлөгч":
    st.markdown("<h1 class='main-title'>Ээлжит хичээл төлөвлөлт</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        file = st.file_uploader("Сурах бичиг (PDF)", type="pdf")
        p_start = st.number_input("Эхлэх хуудас", 1); p_end = st.number_input("Дуусах хуудас", 5)
        tpc = st.text_input("Сэдвийн нэр")
        if st.button("🚀 Төлөвлөгөө гаргах"):
            if file and tpc:
                with st.spinner("AI ажиллаж байна..."):
                    reader = PyPDF2.PdfReader(file)
                    txt = "".join([reader.pages[i].extract_text() for i in range(p_start-1, min(p_end, len(reader.pages)))])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"Сэдэв: {tpc}. Агуулга: {txt[:5000]}. Багшийн төлөвлөгөө гарга."
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    if res.status_code == 200:
                        st.session_state.last_plan = res.json()['choices'][0]['message']['content']
                        save_to_cloud("Төлөвлөгөө", tpc, st.session_state.last_plan)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'last_plan' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.last_plan)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.last_plan), f"{tpc}_plan.docx")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 3. ТЕСТ ҮҮСГЭГЧ ---
elif menu == "📝 Тест үүсгэгч":
    st.markdown("<h1 class='main-title'>Тест үүсгэгч</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t_file = st.file_uploader("PDF оруулах", type="pdf", key="t_up")
        ts = st.number_input("Эхлэх", 1); te = st.number_input("Дуусах", 5)
        t_tpc = st.text_input("Тестийн сэдэв")
        if st.button("🎯 Тест үүсгэх"):
            if t_file and t_tpc:
                with st.spinner("Тест бэлдэж байна..."):
                    reader = PyPDF2.PdfReader(t_file)
                    t_txt = "".join([reader.pages[i].extract_text() for i in range(ts-1, min(te, len(reader.pages)))])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"Текст: {t_txt[:6000]}. Сэдэв: {t_tpc}. Тест бэлд."
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    if res.status_code == 200:
                        st.session_state.last_test = res.json()['choices'][0]['message']['content']
                        save_to_cloud("Тест", t_tpc, st.session_state.last_test)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'last_test' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.last_test)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.last_test), f"{t_tpc}_test.docx")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 4. МИНИЙ САН ---
elif menu == "📊 Миний сан":
    st.markdown("<h1 class='main-title'>Миний Google Drive сан</h1>", unsafe_allow_html=True)
    ps_id = st.session_state.get('personal_sheet_id', '')
    if not ps_id: st.warning("Sidebar-д Sheet ID-гаа оруулна уу.")
    else:
        try:
            client = get_gsheet_client()
            data = client.open_by_key(ps_id).sheet1.get_all_records()
            for item in reversed(data):
                with st.expander(f"📅 {item.get('now', 'Огноо')} | {item.get('doc_type', 'Төрөл')}: {item.get('topic', 'Сэдэв')}"):
                    st.write(item.get('content', 'Хоосон'))
                    st.download_button("📥 Word татах", create_word_doc(item.get('content', '')), f"{item.get('topic')}.docx", key=f"dl_{item.get('now')}")
        except Exception as e: st.error(f"Алдаа: {e}")

# --- AI ЧАТБОТ & ПОРТАЛ (Өмнөх логик хэвээрээ) ---
elif menu == "🤖 AI Чатбот":
    # ... (Өмнөх чатбот код)
    st.markdown("<h1 class='main-title'>Ухаалаг туслах</h1>", unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])
    if prompt := st.chat_input("Асуултаа бичнэ үү..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": st.session_state.messages})
            ans = res.json()['choices'][0]['message']['content']
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})

elif menu == "🌍 Портал":
    t1, t2, t3, t4 = st.tabs(["📚 E-Content", "👨‍🏫 Bagsh.edu.mn", "✅ Үнэлгээ", "📊 EEC Мэдээлэл"])
    with t1: components.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)
    with t2: components.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)
    with t3: components.iframe("https://unelgee.eec.mn/", height=800, scrolling=True)
    with t4: components.iframe("https://www.eec.mn/post/5891", height=800, scrolling=True)
