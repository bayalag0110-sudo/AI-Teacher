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

# --- CUSTOM CSS (Glassmorphism & Theme) ---
if 'theme' not in st.session_state: st.session_state.theme = 'light'

theme_css = {
    'light': {'bg': 'linear-gradient(135deg, #e0f2fe 0%, #bae6fd 50%, #7dd3fc 100%)', 'card': 'rgba(255, 255, 255, 0.7)', 'text': '#1e293b'},
    'dark': {'bg': 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)', 'card': 'rgba(30, 41, 59, 0.7)', 'text': '#f8fafc'}
}
curr = theme_css[st.session_state.theme]

st.markdown(f"""
    <style>
    .stApp {{ background-image: {curr['bg']}; color: {curr['text']}; }}
    .glass-card {{ background: {curr['card']}; backdrop-filter: blur(10px); border-radius: 20px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15); margin-bottom: 20px; }}
    .main-title {{ text-align: center; background: linear-gradient(to right, #2563eb, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 2.5rem; }}
    .stButton>button {{ border-radius: 12px; background: linear-gradient(45deg, #2563eb, #7c3aed); color: white; border: none; padding: 10px 20px; width: 100%; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER WITH WATER EFFECT ---
water_header = f"""
<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 25px; border-radius: 15px; position: relative; overflow: hidden; text-align: center; color: white;">
    <h1 style="margin:0; font-family: 'Poppins', sans-serif;">🌊 EDUPLAN PRO AI</h1>
    <p style="opacity: 0.8;">Мэргэжлийн багшийн ухаалаг туслах</p>
</div>
"""

# --- LOGIN LOGIC ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    components.html(water_header, height=150)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Нэвтрэх код:", type="password")
        if st.button("Нэвтрэх"):
            if pwd == "admin1234":
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Буруу байна!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Тохиргоо")
    if st.button("🌓 Горим солих"):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()
    st.divider()
    menu = st.radio("ЦЭС", ["💎 Төлөвлөгч", "📝 Тест үүсгэгч", "📊 Миний сан", "🌍 Портал"])
    if st.button("🚪 Гарах"):
        st.session_state.authenticated = False
        st.rerun()

# --- 1. ТӨЛӨВЛӨГЧ ---
if menu == "💎 Төлөвлөгч":
    st.markdown("<h1 class='main-title'>Ээлжит хичээл боловсруулах</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        file = st.file_uploader("Сурах бичиг (PDF)", type="pdf")
        l_type = st.selectbox("Хичээлийн хэв шинж", ["Шинэ мэдлэг олгох", "Батгах хичээл", "Лаборатори/Практик", "Шалгалт/Сорил"])
        tpc = st.text_input("Сэдвийн нэр")
        if st.button("🚀 Боловсруулах"):
            if file and tpc:
                with st.spinner("AI төлөвлөгөөг гаргаж байна..."):
                    reader = PyPDF2.PdfReader(file)
                    txt = "".join([p.extract_text() for p in reader.pages[:20]])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"БАТЛАВ: МЕНЕЖЕР Б. НАМУУН\nТөрөл: {l_type}\nСэдэв: {tpc}\nАгуулга: {txt[:5000]}\nСтандарт төлөвлөгөө гарга."
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    if res.status_code == 200:
                        st.session_state.current_plan = res.json()['choices'][0]['message']['content']
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'current_plan' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.current_plan)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 2. ТЕСТ ҮҮСГЭГЧ (ОНОВЧТОЙ & СОНГОЛТТОЙ) ---
elif menu == "📝 Тест үүсгэгч":
    st.markdown("<h1 class='main-title'>Ухаалаг тест үүсгэгч</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t_file = st.file_uploader("Сурах бичиг оруулах", type="pdf", key="t_up")
        t_tpc = st.text_input("Тестийн сэдэв")
        t_format = st.multiselect("Тестийн хэлбэр", 
                                ["Нэг сонголттой (A,B,C,D)", "Олон хариулттай", "Нөхөх даалгавар", "Зөв/Бурууг тогтоох", "Залгамж холбоо тогтоох"],
                                default=["Нэг сонголттой (A,B,C,D)"])
        t_count = st.slider("Асуултын тоо", 5, 20, 10)
        
        if st.button("📝 Тест үүсгэх"):
            if t_file and t_tpc:
                with st.spinner("Зөвхөн сурах бичгийн хүрээнд тест бэлдэж байна..."):
                    reader = PyPDF2.PdfReader(t_file)
                    t_txt = "".join([p.extract_text() for p in reader.pages[:30]])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"""
                    Чи бол боловсролын үнэлгээний мэргэжилтэн.
                    Дараах текстэд тулгуурлан {t_tpc} сэдвээр {t_count} асуулттай тест бэлд.
                    Хэлбэрүүд: {', '.join(t_format)}.
                    Текст: {t_txt[:7000]}
                    Хариултын түлхүүрийг төгсгөлд нь бич.
                    """
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2})
                    if res.status_code == 200:
                        st.session_state.generated_test = res.json()['choices'][0]['message']['content']
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if 'generated_test' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.generated_test)
            doc = Document(); doc.add_paragraph(st.session_state.generated_test)
            bio = BytesIO(); doc.save(bio)
            st.download_button("📥 Тест татах (Word)", bio.getvalue(), "test.docx")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 3. МИНИЙ САН & ПОРТАЛ ---
elif menu == "📊 Миний сан":
    st.info("Тун удахгүй: Таны хадгалсан төлөвлөгөөнүүд энд харагдах болно.")

elif menu == "🌍 Портал":
    tabs = st.tabs(["📚 E-Content", "💻 Medle.mn", "👨‍🏫 Bagsh.edu.mn", "📊 Edumap.mn"])
    with tabs[0]: components.iframe("https://econtent.edu.mn/book", height=800)
    with tabs[1]: components.iframe("https://medle.mn/", height=800)
    with tabs[2]: components.iframe("https://bagsh.edu.mn/", height=800)
    with tabs[3]: components.iframe("https://edumap.mn/", height=800)
