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

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v4.3", layout="wide", page_icon="🎓")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .teacher-header { background: linear-gradient(90deg, #1e3a8a, #3b82f6); padding: 15px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    .student-header { background: linear-gradient(90deg, #064e3b, #10b981); padding: 15px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    .glass-card { background: white; border-radius: 15px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .main-title { text-align: center; font-weight: 800; background: linear-gradient(90deg, #2563eb, #9333ea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
    """, unsafe_allow_html=True)

# --- WORD DOCUMENT GENERATOR ---
def create_word_doc(content, title):
    doc = Document()
    doc.add_heading(title, 0)
    doc.add_paragraph(content)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- LOGIN LOGIC ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='margin-top:80px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1 class='main-title'>EduPlan Pro</h1>", unsafe_allow_html=True)
        u_role = st.selectbox("Та хэн бэ?", ["Багш", "Сурагч"])
        u_name = st.text_input("Нэр:")
        u_class = st.text_input("Анги / Бүлэг (Жишээ нь: 10А):").upper()
        u_pwd = st.text_input("Нууц үг:", type="password")
        if st.button("Нэвтрэх"):
            if u_pwd == "admin1234" and u_name and u_class:
                st.session_state.auth, st.session_state.role, st.session_state.user, st.session_state.u_class = True, u_role, u_name, u_class
                st.rerun()
            else: st.error("Мэдээлэл дутуу байна!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user}")
    st.caption(f"📍 {st.session_state.role} | 🏫 {st.session_state.u_class}")
    if st.session_state.role == "Багш":
        menu = st.radio("ЦЭС", ["💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📝 Даалгавар өгөх", "🤖 AI Чатбот", "🌍 Портал"])
    else:
        menu = st.radio("ЦЭС", ["📚 Миний даалгавар", "📤 Даалгавар илгээх", "🤖 AI Туслах"])
    if st.button("🚪 Гарах"): st.session_state.auth = False; st.rerun()

# --- ТЕСТ ҮҮСГЭГЧ МОДУЛЬ ---
if st.session_state.role == "Багш" and menu == "📝 Тест үүсгэгч":
    st.markdown("<div class='teacher-header'><h1>📝 Тест боловсруулах (AI)</h1></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        t_file = st.file_uploader("Сурах бичиг (PDF)", type="pdf", key="test_pdf")
        t_start = st.number_input("Эхлэх хуудас", 1, value=1)
        t_end = st.number_input("Дуусах хуудас", 1, value=2)
        t_num = st.slider("Асуултын тоо", 5, 20, 10)
        t_type = st.selectbox("Тестийн хэлбэр", ["Олон сонголттой (A,B,C,D)", "Үнэн/Худал", "Нөхөх даалгавар"])
        
        if st.button("🎯 Тест боловсруулах"):
            if t_file:
                with st.spinner("AI агуулгыг уншиж байна..."):
                    reader = PyPDF2.PdfReader(t_file)
                    t_text = "".join([reader.pages[i].extract_text() for i in range(t_start-1, min(t_end, len(reader.pages)))])
                    
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"""Чи бол Монгол улсын боловсролын стандартын дагуу тест боловсруулах мэргэжилтэн.
                    Дараах текст дээр үндэслэн {t_num} ширхэг {t_type} тест боловсруул. 
                    Тестийн төгсгөлд зөв хариултын түлхүүрийг заавал хавсарга.
                    Текст: {t_text[:6000]}"""
                    
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, 
                                      json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    
                    if res.status_code == 200:
                        st.session_state.last_test = res.json()['choices'][0]['message']['content']
                        st.rerun()
            else:
                st.warning("Файлаа оруулна уу!")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if 'last_test' in st.session_state:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader("📋 Боловсруулсан тест")
            st.markdown(st.session_state.last_test)
            st.download_button("📥 Word файл татах", create_word_doc(st.session_state.last_test, "Шалгалтын тест"), "test.docx")
            st.markdown("</div>", unsafe_allow_html=True)

# --- ЭЭЛЖИТ ТӨЛӨВЛӨГӨӨ (Өмнөх логик) ---
elif st.session_state.role == "Багш" and menu == "💎 Ээлжит төлөвлөгч":
    st.markdown("<div class='teacher-header'><h1>💎 Ээлжит хичээл төлөвлөлт</h1></div>", unsafe_allow_html=True)
    # ... (Өмнөх төлөвлөгөөний код энд үргэлжилнэ)

# --- ПОРТАЛ ХЭСЭГ (Өмнөх бүх сайтууд) ---
elif menu == "🌍 Портал":
    st.markdown("<h2 class='main-title'>🌍 Боловсролын нэгдсэн портал</h2>", unsafe_allow_html=True)
    tabs = st.tabs(["📚 E-Content", "👨‍🏫 Bagsh.edu.mn", "✅ Unelgee.eec.mn", "📊 EEC.mn", "📑 Esis.edu.mn"])
    with tabs[0]: components.iframe("https://econtent.edu.mn/book", height=800)
    with tabs[1]: components.iframe("https://bagsh.edu.mn/", height=800)
    with tabs[2]: components.iframe("https://unelgee.eec.mn/", height=800)
    with tabs[3]: components.iframe("https://www.eec.mn/", height=800)
    with tabs[4]: components.iframe("https://esis.edu.mn/", height=800)

# --- AI ЧАТБОТ ---
elif "AI" in menu:
    st.subheader("🤖 AI Туслах")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if p := st.chat_input("Асуултаа бичнэ үү..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": st.session_state.messages})
        ans = res.json()['choices'][0]['message']['content']
        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
