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

# 1. ХУУДАСНЫ ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro AI v2.9", layout="wide", page_icon="🎓")

# --- CUSTOM CSS ---
if 'theme' not in st.session_state: st.session_state.theme = 'light'
curr_theme = {
    'light': {'bg': '#f8fafc', 'card': 'rgba(255, 255, 255, 0.95)', 'text': '#1e293b'},
    'dark': {'bg': '#0f172a', 'card': 'rgba(30, 41, 59, 0.9)', 'text': '#f8fafc'}
}
curr = curr_theme[st.session_state.theme]

st.markdown(f"""
    <style>
    .stApp {{ background-color: {curr['bg']}; color: {curr['text']}; font-family: 'Inter', sans-serif; }}
    .glass-card {{
        background: {curr['card']}; backdrop-filter: blur(15px);
        border-radius: 24px; padding: 30px; border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05); margin-bottom: 20px;
    }}
    .main-title {{
        text-align: center; font-weight: 800; font-size: 2.8rem;
        background: linear-gradient(135deg, #2563eb 0%, #9333ea 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .stButton>button {{
        border-radius: 12px; background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        color: white; border: none; padding: 12px; width: 100%; font-weight: 600;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTION: GOOGLE SHEETS ХОЛБОЛТ ---
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
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        sheet.append_row([now, doc_type, topic, content])
        return True
    except: return False

# --- НЭВТРЭХ ХЭСЭГ ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div style="margin-top:100px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("<h1 class='main-title'>EduPlan Pro</h1>", unsafe_allow_html=True)
        st.write("Багшийн ухаалаг системд нэвтрэх")
        login_pwd = st.text_input("Нууц үг", type="password")
        if st.button("Нэвтрэх"):
            if login_pwd == "admin1234":
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Буруу байна!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Тохиргоо")
    st.session_state.personal_sheet_id = st.text_input("Google Sheet ID", value=st.session_state.get('personal_sheet_id', ''))
    if st.button("🌓 Горим солих"):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()
    st.divider()
    menu = st.radio("ЦЭС", ["🤖 AI Чатбот", "💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📊 Миний сан", "🌍 Портал"])
    if st.button("🚪 Гарах"):
        st.session_state.authenticated = False
        st.rerun()

# --- 1. AI ЧАТБОТ ---
if menu == "🤖 AI Чатбот":
    st.markdown("<h1 class='main-title'>Ухаалаг туслах</h1>", unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])

    if prompt := st.chat_input("Асуултаа энд бичнэ үү..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, 
                                json={"model": "llama-3.3-70b-versatile", "messages": st.session_state.messages})
            ans = res.json()['choices'][0]['message']['content']
            st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

# --- 2. ЭЭЛЖИТ ТӨЛӨВЛӨГӨӨ ---
elif menu == "💎 Ээлжит төлөвлөгч":
    st.markdown("<h1 class='main-title'>Ээлжит хичээл төлөвлөлт</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        file = st.file_uploader("Сурах бичиг (PDF)", type="pdf")
        p_start = st.number_input("Эхлэх хуудас", 1)
        p_end = st.number_input("Дуусах хуудас", 5)
        tpc = st.text_input("Сэдвийн нэр")
        if st.button("🚀 Төлөвлөгөө гаргах"):
            if file and tpc:
                with st.spinner("AI шинжилж байна..."):
                    reader = PyPDF2.PdfReader(file)
                    txt = "".join([reader.pages[i].extract_text() for i in range(p_start-1, min(p_end, len(reader.pages)))])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"Сэдэв: {tpc}. Агуулга: {txt[:5000]}. Стандарт төлөвлөгөө гарга."
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    if res.status_code == 200:
                        content = res.json()['choices'][0]['message']['content']
                        st.session_state.last_plan = content
                        save_to_cloud("Төлөвлөгөө", tpc, content)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'last_plan' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.last_plan); st.markdown('</div>', unsafe_allow_html=True)

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
