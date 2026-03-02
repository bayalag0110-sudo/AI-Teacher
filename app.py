import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v4.7", layout="wide", page_icon="🎓")

# --- CUSTOM CSS (Нэвтрэх хэсэг болон Үндсэн загвар) ---
st.markdown("""
    <style>
    /* Үндсэн дэвсгэр өнгө */
    .stApp {
        background: linear-gradient(135deg, #1e3a8a 0%, #7e22ce 100%);
        background-attachment: fixed;
    }

    /* Нэвтрэх картны загвар (Glassmorphism) */
    .login-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        border-radius: 25px;
        padding: 45px;
        box-shadow: 0 20px 45px rgba(0,0,0,0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-top: 50px;
    }

    /* Дотор талын картууд */
    .glass-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
        color: #1e293b;
    }

    /* Гарчиг болон Текст */
    .main-title {
        text-align: center;
        font-weight: 800;
        font-size: 2.8rem;
        background: linear-gradient(90deg, #1e40af, #9333ea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }

    .teacher-header {
        background: rgba(255, 255, 255, 0.15);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin-bottom: 25px;
    }
    
    /* Товчлуурын загвар */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        padding: 10px;
        transition: 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ФУНКЦҮҮД (Word болон PDF) ---
def create_word_doc(content, title):
    doc = Document()
    doc.add_heading(title, 0)
    doc.add_paragraph(content)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- НЭВТРЭХ ЛОГИК ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    c1, login_col, c2 = st.columns([1, 1.4, 1])
    with login_col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("<h1 class='main-title'>EduPlan Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#475569;'>Боловсролын ухаалаг туслах систем</p>", unsafe_allow_html=True)
        
        u_role = st.radio("Та хэн бэ?", ["Багш", "Сурагч"], horizontal=True)
        u_name = st.text_input("👤 Хэрэглэгчийн нэр")
        
        u_class = ""
        if u_role == "Сурагч":
            u_class = st.text_input("🏫 Анги / Бүлэг").upper()
            
        u_pwd = st.text_input("🔑 Нууц үг", type="password")
        
        if st.button("НЭВТРЭХ"):
            if u_pwd == "admin1234" and u_name:
                if u_role == "Сурагч" and not u_class:
                    st.error("Ангиа оруулна уу!")
                else:
                    st.session_state.auth = True
                    st.session_state.role = u_role
                    st.session_state.user = u_name
                    st.session_state.u_class = u_class
                    st.rerun()
            else:
                st.error("Нэвтрэх мэдээлэл буруу байна!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR МЕНЮ ---
with st.sidebar:
    st.markdown(f"## 👤 {st.session_state.user}")
    st.info(f"📍 {st.session_state.role} " + (f"| 🏫 {st.session_state.u_class}" if st.session_state.u_class else ""))
    st.divider()
    
    if st.session_state.role == "Багш":
        menu = st.radio("ҮНДСЭН ЦЭС", ["💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📝 Даалгавар өгөх", "🤖 AI Чатбот", "🌍 Портал"])
    else:
        menu = st.radio("СУРАГЧИЙН ЦЭС", ["📚 Миний даалгавар", "📤 Даалгавар илгээх", "🤖 AI Туслах"])
        
    if st.button("🚪 Гарах"):
        st.session_state.auth = False
        st.rerun()

# --- МОРФОЛОГИ (АГУУЛГА) ---

# 1. ЭЭЛЖИТ ТӨЛӨВЛӨГӨӨ
if menu == "💎 Ээлжит төлөвлөгч":
    st.markdown("<div class='teacher-header'><h1>💎 Ээлжит хичээл төлөвлөлт</h1></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        p_file = st.file_uploader("Сурах бичиг (PDF)", type="pdf")
        p_start = st.number_input("Эхлэх хуудас", 1, value=1)
        p_end = st.number_input("Дуусах хуудас", 1, value=3)
        p_tpc = st.text_input("Хичээлийн сэдэв")
        if st.button("🚀 Боловсруулах"):
            if p_file and p_tpc:
                with st.spinner("AI төлөвлөгөө гаргаж байна..."):
                    reader = PyPDF2.PdfReader(p_file)
                    txt = "".join([reader.pages[i].extract_text() for i in range(p_start-1, min(p_end, len(reader.pages)))])
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"Сэдэв: {p_tpc}. Текст: {txt[:5000]}. Багшийн ээлжит хичээлийн төлөвлөгөөг заасан стандартын дагуу гарга."}]})
                    st.session_state.last_plan = res.json()['choices'][0]['message']['content']
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        if 'last_plan' in st.session_state:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(st.session_state.last_plan)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.last_plan, p_tpc), f"{p_tpc}.docx")
            st.markdown("</div>", unsafe_allow_html=True)

# 2. ТЕСТ ҮҮСГЭГЧ
elif menu == "📝 Тест үүсгэгч":
    st.markdown("<div class='teacher-header'><h1>📝 Тест боловсруулах</h1></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        t_file = st.file_uploader("PDF оруулах", type="pdf", key="t_pdf")
        t_num = st.slider("Асуултын тоо", 5, 20, 10)
        if st.button("🎯 Тест үүсгэх"):
            if t_file:
                with st.spinner("Асуултууд бэлдэж байна..."):
                    reader = PyPDF2.PdfReader(t_file)
                    txt = "".join([p.extract_text() for p in reader.pages[:3]])
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"Текст: {txt[:5000]}. Энэ агуулгаар {t_num} тест зохиож, хариуг нь төгсгөлд нь бич."}]})
                    st.session_state.last_test = res.json()['choices'][0]['message']['content']
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        if 'last_test' in st.session_state:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(st.session_state.last_test)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.last_test, "Шалгалт"), "test.docx")
            st.markdown("</div>", unsafe_allow_html=True)

# 3. ДААЛГАВАР ӨГӨХ
elif menu == "📝 Даалгавар өгөх":
    st.markdown("<div class='teacher-header'><h1>📝 Сурагчдад даалгавар илгээх</h1></div>", unsafe_allow_html=True)
    with st.form("hw"):
        c_name = st.text_input("Аль ангид?")
        h_title = st.text_input("Гарчиг")
        h_desc = st.text_area("Даалгаврын агуулга")
        if st.form_submit_button("🚀 Нийтлэх"):
            st.success(f"✅ {c_name} ангид даалгавар амжилттай илгээгдлээ.")

# 4. AI ЧАТБОТ
elif "AI" in menu:
    st.markdown("<div class='teacher-header'><h1>🤖 AI Туслах</h1></div>", unsafe_allow_html=True)
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

# 5. ПОРТАЛ
elif menu == "🌍 Портал":
    st.markdown("<div class='teacher-header'><h1>🌍 Боловсролын Порталууд</h1></div>", unsafe_allow_html=True)
    tabs = st.tabs(["📚 E-Content", "👨‍🏫 Bagsh.edu.mn", "✅ Unelgee", "📊 EEC", "📑 ESIS"])
    with tabs[0]: components.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)
    with tabs[1]: components.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)
    with tabs[2]: components.iframe("https://unelgee.eec.mn/", height=800, scrolling=True)
    with tabs[3]: components.iframe("https://www.eec.mn/", height=800, scrolling=True)
    with tabs[4]: st.info("ESIS систем iframe дотор ажиллахгүй тул шууд хаягаар хандана уу: esis.edu.mn")

# 6. СУРАГЧИЙН ХЭСЭГ
elif menu == "📚 Миний даалгавар":
    st.markdown("<div class='teacher-header' style='background: #065f46;'><h1>📚 Миний даалгавар</h1></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='glass-card'><h3>🏫 {st.session_state.u_class} ангийн даалгаврууд</h3><p>Одоогоор ирсэн шинэ даалгавар байхгүй байна.</p></div>", unsafe_allow_html=True)
