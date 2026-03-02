import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
from docx import Document
from io import BytesIO
import PyPDF2

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v5.4", layout="wide", page_icon="🎓")

# --- CUSTOM CSS (Цайвар дэвсгэр болон Текстийн тохиргоо) ---
st.markdown("""
    <style>
    /* Үндсэн дэвсгэр - Цайвар цэнхэр уусалт */
    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        background-attachment: fixed;
    }

    /* Sidebar - Цагаан дэвсгэр, бараан текст */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] * {
        color: #1e293b !important;
    }

    /* Нэвтрэх хэсэг (Glassmorphism - Цайвар) */
    .login-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(15px);
        border-radius: 25px;
        padding: 40px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid rgba(255, 255, 255, 0.5);
        text-align: center;
        margin-top: 20px;
    }
    .login-card h1, .login-card p {
        color: #1e3a8a !important;
    }

    /* Дотор талын цагаан картууд */
    .glass-card {
        background: white !important;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    
    /* Карт доторх бүх текстийг БАРААН болгох (Харагдах байдлыг хангах) */
    .glass-card label, .glass-card p, .glass-card h3, .glass-card span {
        color: #1e293b !important;
        font-weight: 500;
    }

    /* Input талбарууд */
    div.stTextInput input, div.stNumberInput input, div.stSelectbox div {
        color: black !important;
        background-color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
    }

    /* Гол товчлуур */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        font-weight: 700;
        border-radius: 12px;
        border: none;
        padding: 10px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- ТУСЛАХ ФУНКЦҮҮД ---
def create_word_doc(content, title):
    doc = Document()
    doc.add_heading(title, 0)
    doc.add_paragraph(content)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- НЭВТРЭХ ХЭСЭГ ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, login_col, _ = st.columns([1, 1.2, 1])
    with login_col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        try:
            # Таны илгээсэн логоны файл
            st.image('450633998_2213051369057631_4561852154062620515_n.jpg', width=160)
        except:
            st.markdown("<h1 style='font-size:4rem;'>🎓</h1>", unsafe_allow_html=True)
            
        st.markdown("<h1>EduPlan Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p>Замын-Үүд ЕБ-ын 2-р сургууль</p>", unsafe_allow_html=True)
        
        u_role = st.radio("Таны үүрэг:", ["Багш", "Сурагч"], horizontal=True)
        u_name = st.text_input("👤 Хэрэглэгчийн нэр")
        u_pwd = st.text_input("🔑 Нууц үг", type="password")
        
        if st.button("НЭВТРЭХ"):
            if u_pwd == "admin1234" and u_name:
                st.session_state.auth, st.session_state.role, st.session_state.user = True, u_role, u_name
                st.rerun()
            else:
                st.error("Нэр эсвэл нууц үг буруу байна!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR МЕНЮ ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user}")
    st.info(f"Үүрэг: {st.session_state.role}")
    st.divider()
    menu = st.radio("ҮНДСЭН ЦЭС", ["💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📝 Даалгавар өгөх", "🤖 AI Чатбот", "🌍 Портал"])
    if st.button("🚪 Гарах"):
        st.session_state.auth = False
        st.rerun()

# --- МОДУЛИУД ---

if menu == "💎 Ээлжит төлөвлөгч":
    st.markdown("<h1 style='color:#1e3a8a;'>💎 Ээлжит хичээл төлөвлөлт</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        p_file = st.file_uploader("Сурах бичиг (PDF)", type="pdf")
        p_tpc = st.text_input("Хичээлийн сэдэв")
        if st.button("🚀 Төлөвлөгөө гаргах"):
            if p_file and p_tpc:
                with st.spinner("AI боловсруулж байна..."):
                    reader = PyPDF2.PdfReader(p_file)
                    txt = "".join([p.extract_text() for p in reader.pages[:3]])
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"Текст: {txt[:5000]}. Сэдэв: {p_tpc}. Төлөвлөгөө гарга."}]})
                    st.session_state.last_plan = res.json()['choices'][0]['message']['content']
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'last_plan' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.last_plan)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.last_plan, p_tpc), f"{p_tpc}.docx")
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📝 Тест үүсгэгч":
    st.markdown("<h1 style='color:#1e3a8a;'>📝 Тест боловсруулах</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t_file = st.file_uploader("PDF файл", type="pdf", key="t_up")
        t_num = st.slider("Асуултын тоо", 5, 20, 10)
        if st.button("🎯 Тест үүсгэх"):
            if t_file:
                with st.spinner("Асуултууд бэлдэж байна..."):
                    reader = PyPDF2.PdfReader(t_file)
                    txt = "".join([p.extract_text() for p in reader.pages[:2]])
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"Текст: {txt[:5000]}. {t_num} тест зохио."}]})
                    st.session_state.last_test = res.json()['choices'][0]['message']['content']
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'last_test' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.last_test)
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🌍 Портал":
    st.markdown("<h1 style='color:#1e3a8a;'>🌍 Боловсролын Порталууд</h1>", unsafe_allow_html=True)
    tabs = st.tabs(["📚 E-Content", "👨‍🏫 Bagsh.edu.mn", "✅ Unelgee", "📊 EEC"])
    with tabs[0]: components.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)
    with tabs[1]: components.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)
    with tabs[2]: components.iframe("https://unelgee.eec.mn/", height=800, scrolling=True)
    with tabs[3]: components.iframe("https://www.eec.mn/", height=800, scrolling=True)

# AI Чатбот болон Даалгавар хэсэг өмнөх логикоор ажиллана...
