import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v4.5", layout="wide", page_icon="🎓")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .teacher-header { background: linear-gradient(90deg, #1e3a8a, #3b82f6); padding: 15px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    .student-header { background: linear-gradient(90deg, #064e3b, #10b981); padding: 15px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    .glass-card { background: white; border-radius: 15px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .main-title { text-align: center; font-weight: 800; background: linear-gradient(90deg, #2563eb, #9333ea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- WORD ФАЙЛ ҮҮСГЭГЧ ---
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
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='margin-top:80px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1 class='main-title'>EduPlan Pro</h1>", unsafe_allow_html=True)
        u_role = st.radio("Та хэн бэ?", ["Багш", "Сурагч"], horizontal=True)
        u_name = st.text_input("Нэр:")
        u_class = ""
        if u_role == "Сурагч":
            u_class = st.text_input("Анги / Бүлэг (Жишээ нь: 10А):").upper()
        u_pwd = st.text_input("Нууц үг:", type="password")
        if st.button("Нэвтрэх"):
            if u_pwd == "admin1234" and u_name:
                st.session_state.auth, st.session_state.role, st.session_state.user, st.session_state.u_class = True, u_role, u_name, u_class
                st.rerun()
            else: st.error("Мэдээлэл буруу байна!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR МЕНЮ ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user}")
    st.caption(f"📍 {st.session_state.role} " + (f"| 🏫 {st.session_state.u_class}" if st.session_state.u_class else ""))
    st.divider()
    if st.session_state.role == "Багш":
        menu = st.radio("ЦЭС", ["💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📝 Даалгавар өгөх", "🤖 AI Чатбот", "🌍 Портал"])
    else:
        menu = st.radio("ЦЭС", ["📚 Миний даалгавар", "📤 Даалгавар илгээх", "🤖 AI Туслах"])
    if st.button("🚪 Гарах"): st.session_state.auth = False; st.rerun()

# --- 1. 💎 ЭЭЛЖИТ ТӨЛӨВЛӨГӨӨ ---
if menu == "💎 Ээлжит төлөвлөгч":
    st.markdown("<div class='teacher-header'><h1>💎 Ээлжит хичээл төлөвлөлт</h1></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        p_file = st.file_uploader("Сурах бичиг (PDF)", type="pdf", key="plan_pdf")
        p_start = st.number_input("Эхлэх хуудас", 1, value=1)
        p_end = st.number_input("Дуусах хуудас", 1, value=3)
        p_tpc = st.text_input("Сэдвийн нэр")
        if st.button("🚀 Боловсруулах"):
            if p_file and p_tpc:
                with st.spinner("AI ажиллаж байна..."):
                    reader = PyPDF2.PdfReader(p_file)
                    txt = "".join([reader.pages[i].extract_text() for i in range(p_start-1, min(p_end, len(reader.pages)))])
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"Сэдэв: {p_tpc}. Текст: {txt[:5000]}. Хичээлийн төлөвлөгөө гарга."}]})
                    st.session_state.last_plan = res.json()['choices'][0]['message']['content']
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        if 'last_plan' in st.session_state:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(st.session_state.last_plan)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.last_plan, p_tpc), f"{p_tpc}.docx")
            st.markdown("</div>", unsafe_allow_html=True)

# --- 2. 📝 ТЕСТ ҮҮСГЭГЧ ---
elif menu == "📝 Тест үүсгэгч":
    st.markdown("<div class='teacher-header'><h1>📝 Тест боловсруулах (AI)</h1></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        t_file = st.file_uploader("PDF оруулах", type="pdf", key="test_pdf")
        t_start = st.number_input("Хуудас эхлэх", 1, value=1)
        t_end = st.number_input("Хуудас дуусах", 1, value=2)
        t_num = st.slider("Асуултын тоо", 5, 20, 10)
        if st.button("🎯 Тест үүсгэх"):
            if t_file:
                with st.spinner("Тест бэлдэж байна..."):
                    reader = PyPDF2.PdfReader(t_file)
                    txt = "".join([reader.pages[i].extract_text() for i in range(t_start-1, min(t_end, len(reader.pages)))])
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"Текст: {txt[:5000]}. Энэ агуулгаар {t_num} тест зохиож, хариуг хавсарга."}]})
                    st.session_state.last_test = res.json()['choices'][0]['message']['content']
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        if 'last_test' in st.session_state:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(st.session_state.last_test)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.last_test, "Шалгалт"), "test.docx")
            st.markdown("</div>", unsafe_allow_html=True)

# --- 3. 📝 ДААЛГАВАР ӨГӨХ (БАГШ) ---
elif menu == "📝 Даалгавар өгөх":
    st.markdown("<div class='teacher-header'><h1>📝 Даалгавар нийтлэх</h1></div>", unsafe_allow_html=True)
    with st.form("hw_form"):
        t_class = st.text_input("Аль ангид? (Жишээ: 10А)")
        t_title = st.text_input("Гарчиг")
        t_desc = st.text_area("Даалгаврын заавар")
        if st.form_submit_button("🚀 Илгээх"):
            st.success(f"✅ {t_class} ангид даалгавар амжилттай илгээгдлээ.")

# --- 4. 🤖 AI ЧАТБОТ ---
elif menu in ["🤖 AI Чатбот", "🤖 AI Туслах"]:
    st.markdown("<h2 class='main-title'>🤖 EduPlan AI Туслах</h2>", unsafe_allow_html=True)
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

# --- 5. 🌍 ПОРТАЛ ---
elif menu == "🌍 Портал":
    st.markdown("<h2 class='main-title'>🌍 Боловсролын Порталууд</h2>", unsafe_allow_html=True)
    t = st.tabs(["📚 E-Content", "👨‍🏫 Bagsh.edu.mn", "✅ Unelgee", "📊 EEC", "📑 ESIS"])
    with t[0]: components.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)
    with t[1]: components.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)
    with t[2]: components.iframe("https://unelgee.eec.mn/", height=800, scrolling=True)
    with t[3]: components.iframe("https://www.eec.mn/", height=800, scrolling=True)
    with t[4]: st.markdown("ESIS рүү үсрэх: [esis.edu.mn](https://esis.edu.mn/)")

# --- СУРАГЧИЙН ХЭСЭГ ---
elif menu == "📚 Миний даалгавар":
    st.markdown("<div class='student-header'><h1>📚 Миний даалгавар</h1></div>", unsafe_allow_html=True)
    st.info(f"📍 {st.session_state.u_class} ангид одоогоор шинэ даалгавар байхгүй байна.")
