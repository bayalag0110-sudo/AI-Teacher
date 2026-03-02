import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
from docx import Document
from io import BytesIO
import PyPDF2

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v5.3", layout="wide", page_icon="🎓")

# --- CUSTOM CSS (Дэвсгэр өнгө, Лого, Текстийн өнгө) ---
st.markdown("""
    <style>
    /* 1. Үндсэн дэвсгэр (Цайвар уусалт) */
    .stApp {
        background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%); /* Цайвар цэнхэр уусалт */
        background-attachment: fixed;
    }

    /* 2. Нүүрэн хэсгийн текстийг цагаан болгох */
    h1, h2, h3, p, label, .stMarkdown, [data-testid="stSidebar"] * {
        color: #1e293b !important; /* Бараан саарал text */
    }

    /* 3. Нэвтрэх карт (Glassmorphism) */
    .login-card {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 50px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin-top: 40px;
        text-align: center;
    }

    /* 4. Дотор талын картууд (Текст нь хар байх) */
    .glass-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        color: #1e293b;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    .glass-card label, .glass-card p, .glass-card h1, .glass-card h2, .glass-card h3, .glass-card span {
        color: #1e293b !important;
    }

    /* 5. Input талбарууд */
    div.stTextInput input, div.stNumberInput input, div.stSelectbox div {
        color: black !important;
        background-color: #f8fafc !important;
    }
    
    /* 6. Товчлуур */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb, #9333ea);
        color: white;
        font-weight: 700;
        border-radius: 12px;
        padding: 12px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- НЭВТРЭХ ЛОГИК ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    c1, login_col, c2 = st.columns([1, 1.4, 1])
    with login_col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # --- ЛОГО НЭМЭХ ---
        try:
            # Логоны зургийн файлыг 'logo.jpg' гэж нэрлэн код байгаа хавтсанд хадгалаарай
            st.image('logo.jpg', width=120)
        except FileNotFoundError:
            st.markdown("<h1>🎓</h1>", unsafe_allow_html=True)
            
        st.markdown("<h1 style='color: #1e3a8a;'>EduPlan Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color: #475569;'>Боловсролын ухаалаг туслах систем</p>", unsafe_allow_html=True)
        
        u_role = st.radio("Таны үүрэг:", ["Багш", "Сурагч"], horizontal=True)
        u_name = st.text_input("👤 Хэрэглэгчийн нэр")
        u_pwd = st.text_input("🔑 Нууц үг", type="password")
        
        st.write("")
        if st.button("СИСТЕМД НЭВТРЭХ"):
            if u_pwd == "admin1234" and u_name:
                st.session_state.auth = True
                st.session_state.role = u_role
                st.session_state.user = u_name
                st.rerun()
            else:
                st.error("Нэвтрэх мэдээлэл буруу байна!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR (Хажуугийн цэс) ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user}")
    st.caption(f"📍 {st.session_state.role}")
    st.divider()
    
    if st.session_state.role == "Багш":
        menu = st.radio("ҮНДСЭН ЦЭС", ["💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📝 Даалгавар өгөх", "🤖 AI Чатбот", "🌍 Портал"])
    else:
        menu = st.radio("ЦЭС", ["📚 Миний даалгавар", "📤 Даалгавар илгээх", "🤖 AI Туслах"])
        
    if st.button("🚪 Гарах"):
        st.session_state.auth = False
        st.rerun()

# --- МОДУЛИУД (Агуулга) ---
if menu == "💎 Ээлжит төлөвлөгч":
    st.markdown("<h1>💎 Ээлжит хичээл төлөвлөлт</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        p_file = st.file_uploader("Сурах бичиг (PDF)", type="pdf")
        p_tpc = st.text_input("Хичээлийн сэдэв")
        if st.button("🚀 Төлөвлөгөө гаргах"):
            if p_file and p_tpc:
                with st.spinner("AI ажиллаж байна..."):
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"Сэдэв: {p_tpc}. Хичээлийн төлөвлөгөө гарга."}]})
                    st.session_state.last_plan = res.json()['choices'][0]['message']['content']
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        if 'last_plan' in st.session_state:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(st.session_state.last_plan)
            st.markdown("</div>", unsafe_allow_html=True)
