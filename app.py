import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
from docx import Document
from io import BytesIO
import PyPDF2

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v5.5", layout="wide", page_icon="🎓")

# --- CUSTOM CSS (Цайвар уусалт болон текстийн өнгө засалт) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        background-attachment: fixed;
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] * {
        color: #1e293b !important;
    }
    .login-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(15px);
        border-radius: 25px;
        padding: 40px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid rgba(255, 255, 255, 0.5);
        text-align: center;
        margin-top: 20px;
    }
    .glass-card {
        background: white !important;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
        color: #1e293b !important;
    }
    .glass-card label, .glass-card p, .glass-card h3 {
        color: #1e293b !important;
        font-weight: 500;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        font-weight: 700;
        border-radius: 12px;
        border: none;
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
            st.image('450633998_2213051369057631_4561852154062620515_n.jpg', width=160)
        except:
            st.markdown("<h1 style='font-size:4rem;'>🎓</h1>", unsafe_allow_html=True)
        st.markdown("<h1 style='color:#1e3a8a;'>EduPlan Pro</h1>", unsafe_allow_html=True)
        u_name = st.text_input("👤 Нэр")
        u_pwd = st.text_input("🔑 Нууц үг", type="password")
        if st.button("НЭВТРЭХ"):
            if u_pwd == "admin1234" and u_name:
                st.session_state.auth, st.session_state.user = True, u_name
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user}")
    menu = st.radio("ҮНДСЭН ЦЭС", ["💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📝 Даалгавар өгөх", "🤖 AI Чатбот", "🌍 Портал"])
    if st.button("🚪 Гарах"):
        st.session_state.auth = False
        st.rerun()

# --- 1. 💎 ЭЭЛЖИТ ТӨЛӨВЛӨГЧ (PDF Хуудас заах) ---
if menu == "💎 Ээлжит төлөвлөгч":
    st.markdown("<h2 style='color:#1e3a8a;'>💎 Ээлжит хичээл төлөвлөлт</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        p_file = st.file_uploader("Сурах бичиг (PDF)", type="pdf", key="p1")
        p_start = st.number_input("Эхлэх хуудас", 1, value=1)
        p_end = st.number_input("Дуусах хуудас", 1, value=2)
        p_tpc = st.text_input("Хичээлийн сэдэв")
        if st.button("🚀 Төлөвлөгөө боловсруулах"):
            if p_file and p_tpc:
                with st.spinner("AI ажиллаж байна..."):
                    reader = PyPDF2.PdfReader(p_file)
                    txt = "".join([reader.pages[i].extract_text() for i in range(p_start-1, min(p_end, len(reader.pages)))])
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"Текст: {txt[:5000]}. Сэдэв: {p_tpc}. Хичээлийн төлөвлөгөө гарга."}]})
                    st.session_state.last_plan = res.json()['choices'][0]['message']['content']
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'last_plan' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.last_plan)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.last_plan, p_tpc), f"{p_tpc}.docx")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 2. 📝 ТЕСТ ҮҮСГЭГЧ (PDF Хуудас заах) ---
elif menu == "📝 Тест үүсгэгч":
    st.markdown("<h2 style='color:#1e3a8a;'>📝 Тест боловсруулах</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t_file = st.file_uploader("Агуулга (PDF)", type="pdf", key="t1")
        t_start = st.number_input("Эхлэх хуудас", 1, value=1, key="ts")
        t_end = st.number_input("Дуусах хуудас", 1, value=2, key="te")
        t_num = st.slider("Асуултын тоо", 5, 20, 10)
        if st.button("🎯 Тест үүсгэх"):
            if t_file:
                with st.spinner("Асуултууд бэлдэж байна..."):
                    reader = PyPDF2.PdfReader(t_file)
                    txt = "".join([reader.pages[i].extract_text() for i in range(t_start-1, min(t_end, len(reader.pages)))])
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"Текст: {txt[:5000]}. Энэ агуулгаар {t_num} тест зохиож, хариуг хавсарга."}]})
                    st.session_state.last_test = res.json()['choices'][0]['message']['content']
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'last_test' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.last_test)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.last_test, "Тест"), "test.docx")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 3. 📝 ДААЛГАВАР ӨГӨХ ---
elif menu == "📝 Даалгавар өгөх":
    st.markdown("<h2 style='color:#1e3a8a;'>📝 Даалгавар нийтлэх</h2>", unsafe_allow_html=True)
    with st.form("hw_form"):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        hw_class = st.text_input("Аль ангид?")
        hw_title = st.text_input("Гарчиг")
        hw_desc = st.text_area("Зааварчилгаа")
        if st.form_submit_button("🚀 Илгээх"):
            st.success(f"✅ {hw_class} ангид даалгавар амжилттай илгээгдлээ.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 🤖 AI ЧАТБОТ ---
elif menu == "🤖 AI Чатбот":
    st.markdown("<h2 style='color:#1e3a8a;'>🤖 AI Туслах</h2>", unsafe_allow_html=True)
    if "msgs" not in st.session_state: st.session_state.msgs = []
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if p := st.chat_input("Асуух зүйлээ бичнэ үү..."):
        st.session_state.msgs.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                           headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                           json={"model": "llama-3.3-70b-versatile", "messages": st.session_state.msgs})
        ans = res.json()['choices'][0]['message']['content']
        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.msgs.append({"role": "assistant", "content": ans})

# --- 5. 🌍 ПОРТАЛ (Боловсролын сайтууд) ---
elif menu == "🌍 Портал":
    st.markdown("<h2 style='color:#1e3a8a;'>🌍 Боловсролын Порталууд</h2>", unsafe_allow_html=True)
    t = st.tabs(["📚 E-Content", "👨‍🏫 Bagsh.edu.mn", "✅ Unelgee", "📊 EEC", "📑 ESIS"])
    with t[0]: components.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)
    with t[1]: components.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)
    with t[2]: components.iframe("https://unelgee.eec.mn/", height=800, scrolling=True)
    with t[3]: components.iframe("https://www.eec.mn/", height=800, scrolling=True)
    with t[4]: st.info("ESIS систем рүү шууд хандана уу: https://esis.edu.mn/")
