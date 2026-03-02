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
st.set_page_config(page_title="EduPlan Pro v4.2", layout="wide", page_icon="🎓")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .teacher-header { background: linear-gradient(90deg, #1e3a8a, #3b82f6); padding: 15px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    .student-header { background: linear-gradient(90deg, #064e3b, #10b981); padding: 15px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    .glass-card { background: white; border-radius: 15px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .main-title { text-align: center; font-weight: 800; background: linear-gradient(90deg, #2563eb, #9333ea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    /* Iframe-г дэлгэцэнд тааруулах */
    iframe { border-radius: 10px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

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
        menu = st.radio("ЦЭС", ["💎 Ээлжит төлөвлөгч", "📝 Даалгавар өгөх", "📥 Ирсэн даалгавар", "🤖 AI Чатбот", "🌍 Портал"])
    else:
        menu = st.radio("ЦЭС", ["📚 Миний даалгавар", "📤 Даалгавар илгээх", "🤖 AI Туслах"])
    if st.button("🚪 Гарах"): st.session_state.auth = False; st.rerun()

# --- ПОРТАЛ ХЭСЭГ (БҮХ САЙТУУДЫГ НЭГТГЭСЭН) ---
if menu == "🌍 Портал":
    st.markdown("<h2 class='main-title'>🌍 Боловсролын нэгдсэн портал</h2>", unsafe_allow_html=True)
    
    # Портал сайтуудын жагсаалт
    tabs = st.tabs([
        "📚 E-Content", 
        "👨‍🏫 Bagsh.edu.mn", 
        "✅ Unelgee.eec.mn", 
        "📊 EEC.mn", 
        "📑 Esis.edu.mn",
        "🔍 Medeelel.mn"
    ])

    with tabs[0]:
        st.info("📖 Цахим сурах бичиг болон видео хичээлүүд")
        components.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)
    
    with tabs[1]:
        st.info("👨‍🏫 Багшийн хөгжлийн портал")
        components.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)
    
    with tabs[2]:
        st.info("✅ Улсын шалгалтын үнэлгээний систем")
        components.iframe("https://unelgee.eec.mn/", height=800, scrolling=True)
    
    with tabs[3]:
        st.info("📊 Боловсролын үнэлгээний төв (ЭЕШ, мэдээлэл)")
        components.iframe("https://www.eec.mn/", height=800, scrolling=True)

    with tabs[4]:
        st.warning("⚠️ ESIS систем нь аюулгүй байдлын үүднээс iframe дотор ажиллахгүй байж магадгүй. Хэрэв харагдахгүй бол шууд хаягаар хандана уу.")
        st.markdown("[Esis рүү үсрэх](https://esis.edu.mn/dotood)")
        components.iframe("https://esis.edu.mn/dotood", height=800, scrolling=True)

    with tabs[5]:
        st.info("🔍 Боловсролын салбарын статистик мэдээлэл")
        components.iframe("https://medeelel.mn/", height=800, scrolling=True)

# --- БАГШИЙН ХЭСЭГ: ЭЭЛЖИТ ТӨЛӨВЛӨГӨӨ ---
elif st.session_state.role == "Багш" and menu == "💎 Ээлжит төлөвлөгч":
    st.markdown("<div class='teacher-header'><h1>💎 Ээлжит хичээл төлөвлөлт</h1></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        p_file = st.file_uploader("Сурах бичиг (PDF)", type="pdf")
        p_start = st.number_input("Эхлэх хуудас", 1, value=1)
        p_end = st.number_input("Дуусах хуудас", 1, value=3)
        p_tpc = st.text_input("Сэдвийн нэр")
        if st.button("🚀 Боловсруулах"):
            if p_file and p_tpc:
                with st.spinner("AI ажиллаж байна..."):
                    reader = PyPDF2.PdfReader(p_file)
                    p_text = "".join([reader.pages[i].extract_text() for i in range(p_start-1, min(p_end, len(reader.pages)))])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"Чи бол Монголын мэргэжлийн багш. Текст: {p_text[:5000]}. Сэдэв: {p_tpc}. Хичээлийн төлөвлөгөө гарга."
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    if res.status_code == 200:
                        st.session_state.last_plan = res.json()['choices'][0]['message']['content']
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        if 'last_plan' in st.session_state:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(st.session_state.last_plan)
            st.markdown("</div>", unsafe_allow_html=True)

# --- СУРАГЧИЙН ХЭСЭГ: МИНИЙ ДААЛГАВАР ---
elif st.session_state.role == "Сурагч" and menu == "📚 Миний даалгавар":
    st.markdown("<div class='student-header'><h1>📚 Миний даалгавар</h1></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='glass-card'><h3>📘 {st.session_state.u_class} ангид өгөгдсөн даалгаврууд</h3><p>Одоогоор ирсэн даалгавар байхгүй байна.</p></div>", unsafe_allow_html=True)

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

# --- БУСАД ЦЭСҮҮД ---
else:
    st.info("Тун удахгүй...")
