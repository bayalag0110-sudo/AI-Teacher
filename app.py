import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2
import plotly.express as px

# 1. Хуудасны үндсэн тохиргоо
st.set_page_config(page_title="EduPlan Pro AI v2.0", layout="wide", page_icon="🎓")

# --- LIGHT/DARK MODE & GLASSMORPHISM CSS ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

theme_css = {
    'light': {
        'bg': 'linear-gradient(135deg, #e0f2fe 0%, #bae6fd 50%, #7dd3fc 100%)',
        'card': 'rgba(255, 255, 255, 0.7)',
        'text': '#1e293b',
        'sidebar': '#ffffff'
    },
    'dark': {
        'bg': 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
        'card': 'rgba(30, 41, 59, 0.7)',
        'text': '#f8fafc',
        'sidebar': '#1e293b'
    }
}

curr = theme_css[st.session_state.theme]

st.markdown(f"""
    <style>
    .stApp {{ background-image: {curr['bg']}; color: {curr['text']}; }}
    section[data-testid="stSidebar"] {{ background-color: {curr['sidebar']} !important; }}
    
    /* Glassmorphism Card Style */
    .glass-card {{
        background: {curr['card']};
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        margin-bottom: 20px;
    }}
    
    .main-title {{
        text-align: center;
        background: linear-gradient(to right, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
    }}
    
    .stButton>button {{
        border-radius: 12px;
        background: linear-gradient(45deg, #2563eb, #7c3aed);
        color: white;
        border: none;
        padding: 10px 20px;
        transition: 0.3s;
    }}
    .stButton>button:hover {{ transform: scale(1.02); box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4); }}
    </style>
    """, unsafe_allow_html=True)

# --- ANIMATED HEADER ---
header_html = f"""
<div style="text-align: center; padding: 20px;">
    <h1 style="margin:0; font-family: 'Poppins', sans-serif; color: {curr['text']};">🎓 EDUPLAN PRO AI <span style="font-size: 1rem; vertical-align: middle; background: #2563eb; padding: 4px 8px; border-radius: 10px; color: white;">v2.0</span></h1>
    <p style="color: {curr['text']}; opacity: 0.8;">Ухаалаг багшийн туслах систем</p>
</div>
"""

# --- AUTH LOGIC ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    components.html(header_html, height=120)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Нэвтрэх код", type="password")
        if st.button("Системд нэвтрэх"):
            if pwd == "admin1234":
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Буруу байна!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- MAIN NAVIGATION ---
with st.sidebar:
    st.button("🌓 Горим солих", on_click=toggle_theme)
    st.divider()
    menu = st.radio("ҮНДСЭН ЦЭС", ["💎 Ухаалаг төлөвлөгч", "📝 Тест үүсгэгч", "📊 Миний сан", "🌍 Портал"])
    if st.button("🚪 Гарах"):
        st.session_state.authenticated = False
        st.rerun()

# --- 1. УХААЛАГ ТӨЛӨВЛӨГӨӨ ---
if menu == "💎 Ухаалаг төлөвлөгч":
    st.markdown("<h1 class='main-title'>Хичээл төлөвлөлт</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        file = st.file_uploader("PDF сурах бичиг", type="pdf")
        lesson_type = st.selectbox("Хичээлийн хэв шинж", ["Шинэ мэдлэг олгох", "Батгах хичээл", "Лаборатори/Практик"])
        tpc = st.text_input("Сэдвийн нэр")
        
        if st.button("🚀 Төлөвлөгөө боловсруулах"):
            if file and tpc:
                with st.spinner("AI ажиллаж байна..."):
                    reader = PyPDF2.PdfReader(file)
                    txt = "".join([p.extract_text() for p in reader.pages])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"""
                    БАТЛАВ: СУРГАЛТЫН МЕНЕЖЕР Б. НАМУУН
                    Хичээлийн төрөл: {lesson_type}
                    Сэдэв: {tpc}
                    Агуулга: {txt[:5000]}
                    Монгол улсын стандартын дагуу 45 минутын төлөвлөгөөг хүснэгт болон текст хослуулан гарга.
                    """
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                      headers=headers, 
                                      json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    if res.status_code == 200:
                        st.session_state.current_plan = res.json()['choices'][0]['message']['content']
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if 'current_plan' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<div style='text-align:right; font-weight:bold;'>БАТЛАВ: МЕНЕЖЕР Б. НАМУУН</div>", unsafe_allow_html=True)
            st.markdown(st.session_state.current_plan)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 2. ТЕСТ ҮҮСГЭГЧ ---
elif menu == "📝 Тест үүсгэгч":
    st.markdown("<h1 class='main-title'>Автомат тест</h1>", unsafe_allow_html=True)
    tpc_test = st.text_input("Ямар сэдвээр тест бэлдэх үү?")
    if st.button("📝 Тест бэлдэх"):
        headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
        prompt = f"Сэдэв: {tpc_test}. Энэ сэдвээр 5 сонгох асуулттай тест хариултын хамт бэлд."
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                          headers=headers, 
                          json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
        st.write(res.json()['choices'][0]['message']['content'])

# --- ПОРТАЛ ХЭСЭГ ---
elif menu == "🌍 Портал":
    tabs = st.tabs(["E-Content", "Medle.mn", "Bagsh.edu.mn"])
    with tabs[0]: components.iframe("https://econtent.edu.mn/book", height=800)
    with tabs[1]: components.iframe("https://medle.mn/", height=800)
    with tabs[2]: components.iframe("https://bagsh.edu.mn/", height=800)
