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
st.set_page_config(page_title="EduPlan Pro AI v2.9", layout="wide", page_icon="🎓")

# --- CUSTOM CSS (Advanced UI/UX) ---
if 'theme' not in st.session_state: st.session_state.theme = 'light'
curr_theme = {
    'light': {'bg': '#f8fafc', 'card': 'rgba(255, 255, 255, 0.95)', 'text': '#1e293b', 'accent': '#2563eb'},
    'dark': {'bg': '#0f172a', 'card': 'rgba(30, 41, 59, 0.9)', 'text': '#f8fafc', 'accent': '#3b82f6'}
}
curr = curr_theme[st.session_state.theme]

st.markdown(f"""
    <style>
    /* Үндсэн фон болон текст */
    .stApp {{ background-color: {curr['bg']}; color: {curr['text']}; font-family: 'Inter', sans-serif; }}
    
    /* Шилэн картууд */
    .glass-card {{
        background: {curr['card']};
        backdrop-filter: blur(15px);
        border-radius: 24px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }}
    
    /* Нэвтрэх хэсгийн тусгай дизайн */
    .login-container {{
        max-width: 450px;
        margin: 100px auto;
        text-align: center;
    }}
    
    .main-title {{
        font-weight: 800;
        font-size: 3rem;
        background: linear-gradient(135deg, #2563eb 0%, #9333ea 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }}

    /* Товчлуурын дизайн */
    .stButton>button {{
        border-radius: 14px;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        color: white;
        border: none;
        padding: 14px 28px;
        width: 100%;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.5);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- НЭВТРЭХ ХЭСЭГ (RE-DESIGNED) ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>EduPlan Pro</h1>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2997/2997300.png", width=80)
    st.subheader("Системд нэвтрэх")
    st.caption("Багшийн ухаалаг туслах v2.9")
    
    login_pwd = st.text_input("Нэвтрэх код", type="password", placeholder="••••••••")
    
    if st.button("Нэвтрэх"):
        if login_pwd == "admin1234":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Нууц үг буруу байна. Дахин оролдоно уу.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<p style='opacity:0.6; font-size:0.8rem;'>© 2024 EduPlan AI Technology. All rights reserved.</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR & NAVIGATION ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.get('teacher_name', 'Багш')}")
    personal_sheet_id = st.text_input("Google Sheet ID", key="ps_id")
    if st.button("🌓 Горим солих"):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()
    st.divider()
    menu = st.radio("ЦЭС", ["🤖 AI Чатбот", "💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📊 Миний сан", "🌍 Портал"])
    if st.button("🚪 Системээс гарах"):
        st.session_state.authenticated = False
        st.rerun()

# --- FUNCTION: GOOGLE SHEETS SAVE ---
def save_to_cloud(doc_type, topic, content):
    if not personal_sheet_id: return False
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(personal_sheet_id).sheet1
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        sheet.append_row([now, doc_type, topic, content])
        return True
    except: return False

# --- 1. ЭЭЛЖИТ ТӨЛӨВЛӨГӨӨ (ХУУДАС ЗААДАГ ФУНКЦТАЙ) ---
if menu == "💎 Ээлжит төлөвлөгч":
    st.markdown("<h1 class='main-title'>Ээлжит хичээл төлөвлөлт</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        p_file = st.file_uploader("Сурах бичиг (PDF)", type="pdf", key="plan_pdf")
        
        st.write("📖 Хичээлийн агуулга бүхий хуудас:")
        c_p1, c_p2 = st.columns(2)
        with c_p1: p_start = st.number_input("Эхлэх", min_value=1, value=1, key="ps")
        with c_p2: p_end = st.number_input("Дуусах", min_value=1, value=3, key="pe")
            
        p_tpc = st.text_input("Сэдвийн нэр", placeholder="Жишээ: Мэдээлэл ба объект")
        p_type = st.selectbox("Хичээлийн хэв шинж", ["Шинэ мэдлэг", "Батгах", "Дадлага", "Сорил"])
        
        if st.button("🚀 Төлөвлөгөө боловсруулах"):
            if p_file and p_tpc:
                with st.spinner("AI текстийг шинжилж байна..."):
                    reader = PyPDF2.PdfReader(p_file)
                    # Заасан хуудсуудын текстийг салгах
                    p_text = ""
                    for i in range(p_start-1, min(p_end, len(reader.pages))):
                        p_text += reader.pages[i].extract_text()
                    
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"Чи бол мэргэжлийн багш. Дараах текстийг ашиглан {p_tpc} сэдвийн {p_type} хичээлийн 45 минутын төлөвлөгөөг Монгол улсын стандартын дагуу гарга. Текст: {p_text[:6000]}"
                    
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, 
                                      json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    if res.status_code == 200:
                        st.session_state.plan_result = res.json()['choices'][0]['message']['content']
                        save_to_cloud("Төлөвлөгөө", p_tpc, st.session_state.plan_result)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if 'plan_result' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader(f"✅ {p_tpc} - Хичээлийн төлөвлөгөө")
            st.markdown(st.session_state.plan_result)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 2. БУСАД ЦЭСҮҮД (Чатбот, Тест, Миний сан, Портал өмнөх логикоор үргэлжилнэ) ---
# ... (Кодны үлдсэн хэсэг нь өмнөх хувилбартай ижил логикоор ажиллана)
