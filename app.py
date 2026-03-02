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
st.set_page_config(page_title="EduPlan Pro v4.0", layout="wide", page_icon="🎓")

# --- CUSTOM CSS (БАГШ БОЛОН СУРАГЧИЙН ӨНГӨ ЯЛГАА) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .teacher-header { background: linear-gradient(90deg, #1e3a8a, #3b82f6); padding: 20px; border-radius: 15px; color: white; text-align: center; }
    .student-header { background: linear-gradient(90deg, #064e3b, #10b981); padding: 20px; border-radius: 15px; color: white; text-align: center; }
    .card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); margin-bottom: 15px; border-top: 4px solid #3b82f6; }
    .stat-box { background: #eff6ff; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #bfdbfe; }
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE SHEETS API ХОЛБОЛТ ---
def get_gsheet_client():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds)
    except:
        st.error("Google Sheets тохиргоо (Secrets) дутуу байна!")
        return None

# --- НЭВТРЭХ ЛОГИК ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center;'>EduPlan AI 🎓</h1>", unsafe_allow_html=True)
        role = st.selectbox("Та хэн бэ?", ["Багш", "Сурагч"])
        u_name = st.text_input("Таны нэр:")
        u_class = st.text_input("Анги / Бүлэг (Жишээ нь: 10А, 9Б):").upper()
        u_pwd = st.text_input("Нууц үг:", type="password")
        
        if st.button("Нэвтрэх"):
            if u_pwd == "admin1234" and u_name and u_class:
                st.session_state.auth = True
                st.session_state.role = role
                st.session_state.user = u_name
                st.session_state.u_class = u_class
                st.rerun()
            else: st.warning("Мэдээллээ бүрэн оруулна уу.")
    st.stop()

# --- SIDEBAR МЕНЮ ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user}")
    st.info(f"📍 {st.session_state.role} | 🏫 {st.session_state.u_class}")
    st.divider()
    
    if st.session_state.role == "Багш":
        menu = st.radio("ЦЭС", ["📊 Хянах самбар", "📝 Даалгавар өгөх", "📥 Ирсэн даалгавар", "🤖 AI Чатбот", "🌍 Портал"])
    else:
        menu = st.radio("ЦЭС", ["📚 Миний даалгавар", "📤 Даалгавар илгээх", "🤖 AI Туслах"])
    
    if st.button("🚪 Гарах"):
        st.session_state.auth = False
        st.rerun()

# --- БАГШИЙН ҮЙЛДЛҮҮД ---
if st.session_state.role == "Багш":
    st.markdown(f"<div class='teacher-header'><h1>Багшийн Удирдлага</h1><p>{st.session_state.u_class} бүлэг</p></div>", unsafe_allow_html=True)
    st.divider()

    if menu == "📊 Хянах самбар":
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown("<div class='stat-box'><h3>Өгсөн даалгавар</h3><h1>5</h1></div>", unsafe_allow_html=True)
        with c2: st.markdown("<div class='stat-box'><h3>Ирсэн хариу</h3><h1>12</h1></div>", unsafe_allow_html=True)
        with c3: st.markdown("<div class='stat-box'><h3>Шалгаагүй</h3><h1>3</h1></div>", unsafe_allow_html=True)

    elif menu == "📝 Даалгавар өгөх":
        st.subheader("🆕 Шинэ даалгавар нийтлэх")
        with st.form("hw_form"):
            t_title = st.text_input("Даалгаврын гарчиг")
            t_desc = st.text_area("Зааварчилгаа")
            t_date = st.date_input("Дуусах хугацаа")
            if st.form_submit_button("Сурагчид руу илгээх"):
                # Энд Google Sheet рүү хадгалах логик орно
                st.success(f"✅ {st.session_state.u_class} ангийн сурагчдад даалгавар илгээгдлээ.")

    elif menu == "📥 Ирсэн даалгавар":
        st.subheader("📥 Сурагчдын ирүүлсэн материалууд")
        # Жишээ өгөгдөл
        sample_subs = [{"name": "А.Болд", "class": st.session_state.u_class, "title": "Математик - Бие даалт", "time": "14:20"}]
        for s in sample_subs:
            with st.container():
                st.markdown(f"<div class='card'><b>Сурагч:</b> {s['name']} | <b>Анги:</b> {s['class']}<br><b>Сэдэв:</b> {s['title']}</div>", unsafe_allow_html=True)
                st.button(f"Шалгах ({s['name']})")

# --- СУРАГЧИЙН ҮЙЛДЛҮҮД ---
elif st.session_state.role == "Сурагч":
    st.markdown(f"<div class='student-header'><h1>Сурагчийн Портал</h1><p>{st.session_state.u_class} бүлэг</p></div>", unsafe_allow_html=True)
    st.divider()

    if menu == "📚 Миний даалгавар":
        st.subheader(f"📖 {st.session_state.u_class} ангид өгөгдсөн даалгаврууд")
        # Энд зөвхөн тухайн сурагчийн ангид хамаарах даалгаврыг шүүж харуулна
        st.markdown(f"""
        <div class='card'>
            <h3>📗 Функц ба график</h3>
            <p>Багш: Б. Бат-Эрдэнэ</p>
            <p>Заавар: Сурах бичгийн 45-р хуудсыг бодоод зургаар илгээнэ үү.</p>
            <p style='color:red;'>⏰ Хугацаа: 2024-05-25</p>
        </div>
        """, unsafe_allow_html=True)

    elif menu == "📤 Даалгавар илгээх":
        st.subheader("📤 Даалгавар илгээх")
        target_hw = st.selectbox("Даалгавар сонгох", ["Функц ба график", "Объект хандалтат технологи"])
        answer = st.text_area("Хариулт эсвэл тайлбар")
        up_file = st.file_uploader("Файл хавсаргах", type=["pdf", "jpg", "png"])
        if st.button("Багш руу илгээх"):
            st.balloons()
            st.success("🚀 Даалгавар амжилттай илгээгдлээ!")

# --- НЭГДСЭН AI ЧАТБОТ ---
if "AI" in menu:
    st.subheader("🤖 EduPlan AI Туслах")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if p := st.chat_input("Асуултаа бичнэ үү..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, 
                            json={"model": "llama-3.3-70b-versatile", "messages": st.session_state.messages})
        ans = res.json()['choices'][0]['message']['content']
        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

# --- ПОРТАЛ ХЭСЭГ (Зөвхөн Багшид) ---
if menu == "🌍 Портал":
    t1, t2, t3 = st.tabs(["📚 E-Content", "✅ Үнэлгээ", "📊 EEC"])
    with t1: components.iframe("https://econtent.edu.mn/book", height=700)
    with t2: components.iframe("https://unelgee.eec.mn/", height=700)
    with t3: components.iframe("https://www.eec.mn/post/5891", height=700)
