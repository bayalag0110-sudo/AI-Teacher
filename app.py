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

# 1. Хуудасны үндсэн тохиргоо
st.set_page_config(page_title="EduPlan Pro AI v2.8", layout="wide", page_icon="🎓")

# --- GOOGLE SHEETS ХОЛБОЛТ ---
def save_to_personal_sheet(sheet_id, doc_type, topic, content):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).sheet1
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        sheet.append_row([now, doc_type, topic, content])
        return True
    except Exception as e:
        st.error(f"Хадгалахад алдаа гарлаа: {e}")
        return False

# --- CUSTOM CSS ---
if 'theme' not in st.session_state: st.session_state.theme = 'light'
curr_theme = {
    'light': {'bg': 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)', 'card': 'rgba(255, 255, 255, 0.9)', 'text': '#0f172a'},
    'dark': {'bg': 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', 'card': 'rgba(30, 41, 59, 0.8)', 'text': '#f8fafc'}
}
curr = curr_theme[st.session_state.theme]

st.markdown(f"""
    <style>
    .stApp {{ background-image: {curr['bg']}; color: {curr['text']}; }}
    .glass-card {{ background: {curr['card']}; backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; }}
    .main-title {{ text-align: center; color: #2563eb; font-weight: 800; font-size: 2.5rem; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Нэвтрэх код:", type="password")
        if st.button("Нэвтрэх"):
            if pwd == "admin1234": st.session_state.authenticated = True; st.rerun()
            else: st.error("Буруу!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Тохиргоо")
    teacher_name = st.text_input("Багшийн нэр:", value="Б. Багш")
    ps_id = st.text_input("Google Sheet ID:", help="Sheet-ээ Share хийхээ мартав аа!")
    if st.button("🌓 Горим солих"):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'; st.rerun()
    
    st.divider()
    menu = st.radio("ЦЭС", ["🤖 AI Чатбот", "💎 Төлөвлөгч", "📝 Тест үүсгэгч", "📊 Миний сан", "🌍 Портал"])
    if st.button("🚪 Гарах"): st.session_state.authenticated = False; st.rerun()

# --- 1. AI ЧАТБОТ (ШИНЭ) ---
if menu == "🤖 AI Чатбот":
    st.markdown("<h1 class='main-title'>Ухаалаг туслах</h1>", unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Яаж туслах вэ?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, 
                                json={"model": "llama-3.3-70b-versatile", "messages": st.session_state.messages})
            response = res.json()['choices'][0]['message']['content']
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- 2. ТӨЛӨВЛӨГЧ ---
elif menu == "💎 Төлөвлөгч":
    st.markdown("<h1 class='main-title'>Хичээл төлөвлөлт</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        file = st.file_uploader("PDF оруулах", type="pdf")
        tpc = st.text_input("Сэдвийн нэр")
        if st.button("🚀 Боловсруулах"):
            if file and tpc:
                with st.spinner("AI ажиллаж байна..."):
                    reader = PyPDF2.PdfReader(file)
                    txt = "".join([p.extract_text() for p in reader.pages[:10]])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    ai_prompt = f"Сэдэв: {tpc}. Энэ сэдвээр 45 минутын төлөвлөгөө гарга. Агуулга: {txt[:4000]}"
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": ai_prompt}]})
                    if res.status_code == 200:
                        content = res.json()['choices'][0]['message']['content']
                        st.session_state.curr_plan = content
                        if ps_id: save_to_personal_sheet(ps_id, "Төлөвлөгөө", tpc, content)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'curr_plan' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.curr_plan); st.markdown('</div>', unsafe_allow_html=True)

# --- 3. ТЕСТ ҮҮСГЭГЧ ---
elif menu == "📝 Тест үүсгэгч":
    st.markdown("<h1 class='main-title'>Тест үүсгэгч</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t_file = st.file_uploader("PDF оруулах", type="pdf")
        s_p = st.number_input("Эхлэх хуудас", 1); e_p = st.number_input("Дуусах хуудас", 5)
        t_tpc = st.text_input("Сэдэв")
        if st.button("🎯 Тест үүсгэх"):
            if t_file and t_tpc:
                with st.spinner("Тест бэлдэж байна..."):
                    reader = PyPDF2.PdfReader(t_file)
                    t_txt = "".join([reader.pages[i].extract_text() for i in range(s_p-1, min(e_p, len(reader.pages)))])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    ai_prompt = f"Текстэд тулгуурлан {t_tpc} сэдвээр тест бэлд. Текст: {t_txt[:6000]}"
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": ai_prompt}], "temperature": 0.1})
                    if res.status_code == 200:
                        content = res.json()['choices'][0]['message']['content']
                        st.session_state.curr_test = content
                        if ps_id: save_to_personal_sheet(ps_id, "Тест", t_tpc, content)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'curr_test' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.curr_test); st.markdown('</div>', unsafe_allow_html=True)

# --- 4. МИНИЙ САН ---
elif menu == "📊 Миний сан":
    st.markdown("<h1 class='main-title'>Миний Google Drive сан</h1>", unsafe_allow_html=True)
    if not ps_id: st.warning("Sidebar-д Sheet ID-гаа оруулна уу.")
    else:
        try:
            scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
            client = gspread.authorize(creds)
            data = client.open_by_key(ps_id).sheet1.get_all_records()
            for item in reversed(data):
                with st.expander(f"📅 {item.get('now', 'Огноо')} | 📌 {item.get('doc_type', 'Төрөл')}: {item.get('topic', 'Сэдэв')}"):
                    st.markdown(item.get('content', 'Хоосон'))
        except: st.error("ID буруу эсвэл эрх өгөөгүй байна.")

# --- 5. ПОРТАЛ ---
elif menu == "🌍 Портал":
    tabs = st.tabs(["📚 E-Content", "👨‍🏫 Bagsh.edu.mn", "✅ Үнэлгээ (eec.mn)", "📊 EEC Мэдээлэл"])
    with tabs[0]: components.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)
    with tabs[1]: components.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)
    with tabs[2]: components.iframe("https://unelgee.eec.mn/", height=800, scrolling=True)
    with tabs[3]: components.iframe("https://www.eec.mn/post/5891", height=800, scrolling=True)
