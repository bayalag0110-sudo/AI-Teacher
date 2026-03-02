import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v6.3", layout="wide", page_icon="🎓")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); }
    .glass-card {
        background: white !important;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    label, p, h1, h2, h3, span { color: #1e293b !important; font-weight: 500; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        font-weight: 700;
        border-radius: 10px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ТУСЛАХ ФУНКЦҮҮД ---
def extract_pdf_text(file, start, end):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for i in range(start-1, min(end, len(reader.pages))):
            text += reader.pages[i].extract_text()
        return text
    except: return ""

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
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div class="glass-card" style="text-align:center; margin-top:50px;">', unsafe_allow_html=True)
        st.title("🎓 EduPlan Pro")
        u_pwd = st.text_input("🔑 Нууц үг", type="password")
        if st.button("НЭВТРЭХ"):
            if u_pwd == "admin1234": st.session_state.auth = True; st.rerun()
    st.stop()

# --- SIDEBAR МЕНЮ ---
with st.sidebar:
    menu = st.radio("ҮНДСЭН ЦЭС", ["💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📝 Даалгавар үүсгэх", "🤖 AI Чатбот", "🌍 Портал"])
    if st.button("🚪 Гарах"): st.session_state.auth = False; st.rerun()

# --- 1. 💎 ЭЭЛЖИТ ТӨЛӨВЛӨГЧ (ЗАГВАРЫН ДАГУУ) ---
if menu == "💎 Ээлжит төлөвлөгч":
    st.title("💎 Ээлжит хичээлийн төлөвлөлт")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        p_file = st.file_uploader("Сурах бичиг (PDF)", type="pdf")
        p_pages = st.slider("Хуудас", 1, 500, (1, 3))
        subj = st.text_input("Хичээл", value="Мэдээллийн технологи")
        topic = st.text_input("Сэдэв", placeholder="Сэдвийн нэр...")
        if st.button("🚀 Төлөвлөгөө гаргах"):
            with st.spinner("AI боловсруулж байна..."):
                pdf_text = extract_pdf_text(p_file, p_pages[0], p_pages[1]) if p_file else ""
                prompt = f"""
                Монгол улсын ЕБС-ийн багшийн төлөвлөгөө гаргах загварт тулгуурлан ХҮСНЭГТЭН хэлбэрээр боловсруул:
                Хичээл: {subj}, Сэдэв: {topic}
                Суралцахуйн зорилт: Bloom taxonomy-ийн дагуу.
                
                Хүснэгтийн баганууд:
                - Үе шат (Эхлэл, Өрнөл, Төгсгөл)
                - Хугацаа
                - Суралцахуйн үйл ажиллагаа
                - Багшийн дэмжлэг
                - Хэрэглэгдэхүүн
                
                Мөн:
                - 3 түвшний даалгавар (Дутуу, Эзэмшиж буй, Бүрэн эзэмшсэн)
                - 5 минутын асуулт/даалгавар
                - Гэрийн даалгавар ба Ялгаатай сурагчидтай ажиллах аргачлал.
                """
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                   headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                   json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                st.session_state.plan_res = res.json()['choices'][0]['message']['content']
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'plan_res' in st.session_state:
            st.markdown(f'<div class="glass-card">{st.session_state.plan_res}</div>', unsafe_allow_html=True)

# --- 2. 📝 ДААЛГАВАР ҮҮСГЭХ (АЖИЛЛАДАГ БОЛГОСОН) ---
elif menu == "📝 Даалгавар үүсгэх":
    st.title("📝 Даалгавар боловсруулах")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        hw_topic = st.text_input("Даалгаврын сэдэв")
        hw_type = st.selectbox("Төрөл", ["Гэрийн даалгавар", "Бие даалт", "Шалгалт"])
        if st.button("✨ Даалгавар үүсгэх"):
            with st.spinner("AI ажиллаж байна..."):
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                   headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                   json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"{hw_topic} сэдвээр {hw_type} боловсруулж өг."}]})
                st.session_state.hw_res = res.json()['choices'][0]['message']['content']
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'hw_res' in st.session_state:
            st.markdown(f'<div class="glass-card">{st.session_state.hw_res}</div>', unsafe_allow_html=True)

# --- 3. 🌍 ПОРТАЛ (Бүх сайтууд нэг дор) ---
elif menu == "🌍 Портал":
    st.title("🌍 Боловсролын Порталууд")
    sites = {
        "🗺️ EduMap": "https://edumap.mn/",
        "🎥 Medle": "https://medle.mn/",
        "🎮 Eduten": "https://www.eduten.com/",
        "🇬🇧 Pearson": "https://englishconnect.pearson.com/",
        "📝 Unelgee": "https://unelgee.eec.mn/auth/login/",
        "📚 E-Content": "https://econtent.edu.mn/book",
        "👨‍🏫 Bagsh": "https://bagsh.edu.mn/",
        "📊 EEC": "https://www.eec.mn/"
    }
    t = st.tabs(list(sites.keys()))
    for i, (name, url) in enumerate(sites.items()):
        with t[i]: components.iframe(url, height=800)

# --- 4. 🤖 AI ЧАТБОТ (PDF/Excel уншигчтай) ---
elif menu == "🤖 AI Чатбот":
    st.title("🤖 AI Ухаалаг туслах")
    if "msgs" not in st.session_state: st.session_state.msgs = []
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if p := st.chat_input("Асуултаа бичнэ үү..."):
        st.session_state.msgs.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                           headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                           json={"model": "llama-3.3-70b-versatile", "messages": st.session_state.msgs})
        ans = res.json()['choices'][0]['message']['content']
        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.msgs.append({"role": "assistant", "content": ans})

# 5. ТЕСТ ҮҮСГЭГЧ (Хуучин хэвээр)
elif menu == "📝 Тест үүсгэгч":
    st.title("📝 Тест боловсруулах")
    t_file = st.file_uploader("Файл", type="pdf")
    if st.button("Тест гаргах"):
        st.info("AI ажиллаж байна...")
