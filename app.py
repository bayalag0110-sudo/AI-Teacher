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
st.set_page_config(page_title="EduPlan Pro AI", layout="wide", page_icon="🎓")

# --- HTML/CSS АНИМАЦИ (Таны ирүүлсэн код) ---
water_effect_html = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    body {
        margin: 0;
        padding: 0;
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        overflow: hidden;
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .water-container { position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
    .wave { position: absolute; bottom: 0; left: 0; width: 200%; height: 120px; 
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 120"><path d="M0,60 Q300,0 600,60 T1200,60 L1200,120 L0,120 Z" fill="%23ffffff" opacity="0.3"/></svg>') repeat-x;
        animation: wave 15s linear infinite; }
    .wave:nth-child(2) { bottom: 10px; opacity: 0.5; animation: wave 10s linear infinite reverse;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 120"><path d="M0,60 Q300,20 600,60 T1200,60 L1200,120 L0,120 Z" fill="%2364b5f6" opacity="0.4"/></svg>') repeat-x; }
    .wave:nth-child(3) { bottom: 20px; opacity: 0.3; animation: wave 8s linear infinite;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 120"><path d="M0,60 Q300,40 600,60 T1200,60 L1200,120 L0,120 Z" fill="%2342a5f5" opacity="0.3"/></svg>') repeat-x; }
    @keyframes wave { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
    .content { position: relative; z-index: 10; text-align: center; color: white; animation: fadeInUp 1s ease-out; }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
    .bubble { position: absolute; bottom: 0; background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.8), rgba(100,181,246,0.2)); border-radius: 50%; opacity: 0; animation: float 6s ease-in-out infinite; }
    @keyframes float { 0% { transform: translateY(0) translateX(0); opacity: 1; } 100% { transform: translateY(-100vh) translateX(100px); opacity: 0; } }
    .bubble:nth-child(1) { width: 60px; height: 60px; left: 10%; animation-duration: 8s; }
    .bubble:nth-child(2) { width: 40px; height: 40px; left: 20%; animation-delay: 2s; animation-duration: 7s; }
    .bubble:nth-child(3) { width: 50px; height: 50px; left: 50%; animation-delay: 4s; animation-duration: 9s; }
    h1 { font-size: 3rem; margin-bottom: 10px; text-shadow: 0 4px 20px rgba(0,0,0,0.3); }
    p { font-size: 1.2rem; font-weight: 300; }
</style>
<div class="water-container">
    <div class="bubble"></div><div class="bubble"></div><div class="bubble"></div>
    <div class="content">
        <h1> EDUPLAN PRO AI</h1>
        <p>ЭЭЛЖИТ ХИЧЭЭЛ БОЛОВСРУУЛАХ ВЕБ САЙТАД ТАВТАЙ МОРИЛНО УУ.</p>
    </div>
    <div class="wave"></div><div class="wave"></div><div class="wave"></div>
</div>
"""

# --- CUSTOM STREAMLIT CSS ---
st.markdown("""
    <style>
    .main { background: transparent; }
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    .approval-box { text-align: right; font-family: 'Times New Roman', serif; font-weight: bold; }
    .stButton>button { border-radius: 8px; background-image: linear-gradient(to right, #2563eb, #1d4ed8); color: white; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- НЭВТРЭХ ХЭСЭГ ---
def auth_ui():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        # Усны анимацийг дээд талд харуулах
        components.html(water_effect_html, height=400)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown("<h3 style='text-align:center;'>Нэвтрэх</h3>", unsafe_allow_html=True)
            password = st.text_input("Нууц үг:", type="password")
            if st.button("Нэвтрэх"):
                if password == "admin1234":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Нууц үг буруу!")
        return False
    return True

if auth_ui():
    if 'history' not in st.session_state: st.session_state.history = []

    # --- SIDEBAR & CONTENT ---
    with st.sidebar:
        st.markdown("### ✨ Сайн байна уу, Багшаа")
        if st.button("🚪 Гарах"):
            st.session_state.authenticated = False
            st.rerun()
        menu = st.radio("ЦЭС", ["💎 Төлөвлөгч", "📊 Анализ", "🌍 Портал"])

    if menu == "💎 Төлөвлөгч":
        st.markdown("<h2 style='text-align:center; color:#1E3A8A;'>ЭЭЛЖИТ ХИЧЭЭЛ БОЛОВСРУУЛАХ</h2>", unsafe_allow_html=True)
        col_in, col_out = st.columns([1, 1.3])
        
        with col_in:
            with st.container(border=True):
                file = st.file_uploader("PDF оруулах", type="pdf")
                tpc = st.text_input("Сэдэв")
                if st.button("🚀 Боловсруулах"):
                    if file and tpc:
                        with st.spinner("AI ажиллаж байна..."):
                            reader = PyPDF2.PdfReader(file)
                            txt = "".join([p.extract_text() for p in reader.pages])
                            headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                            prompt = f"БАТЛАВ: СУРГАЛТЫН МЕНЕЖЕР Б. НАМУУН\n\nСэдэв: {tpc}\nАгуулга: {txt[:5000]}"
                            res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                              headers=headers, 
                                              json={"model": "llama-3.3-70b-versatile", 
                                                    "messages": [{"role": "user", "content": prompt}]})
                            if res.status_code == 200:
                                st.session_state.current_view = res.json()['choices'][0]['message']['content']
                                st.rerun()

        with col_out:
            if 'current_view' in st.session_state:
                st.markdown("<div class='approval-box'>БАТЛАВ<br>СУРГАЛТЫН МЕНЕЖЕР ................... Б. НАМУУН</div>", unsafe_allow_html=True)
                st.markdown(st.session_state.current_view)

