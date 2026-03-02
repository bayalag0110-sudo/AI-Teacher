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

# 1. ХУУДАСНЫ ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v3.5", layout="wide", page_icon="🎓")

# --- СИСТЕМИЙН САН (Түр зуур Session-д хадгалах, Cloud-тай холбож болно) ---
if 'homeworks' not in st.session_state:
    st.session_state.homeworks = [] # Багшийн өгсөн даалгаврууд
if 'submissions' not in st.session_state:
    st.session_state.submissions = [] # Сурагчдын илгээсэн хариунууд

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .main-title { text-align: center; color: #1e3a8a; font-weight: 800; font-size: 2.2rem; margin-bottom: 20px; }
    .card { background: white; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 5px solid #3b82f6; }
    .student-card { border-left: 5px solid #10b981; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN LOGIC ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='margin-top:100px;'></div>", unsafe_allow_html=True)
        st.markdown("<h1 class='main-title'>EduPlan Portal</h1>", unsafe_allow_html=True)
        role = st.selectbox("Та хэн бэ?", ["Багш", "Сурагч"])
        user_name = st.text_input("Нэр:")
        pwd = st.text_input("Нууц үг:", type="password")
        if st.button("Нэвтрэх"):
            if pwd == "admin1234" and user_name:
                st.session_state.auth = True
                st.session_state.role = role
                st.session_state.user = user_name
                st.rerun()
            else: st.error("Мэдээлэл дутуу байна!")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user} ({st.session_state.role})")
    st.write(f"📅 {datetime.date.today()}")
    st.divider()
    if st.session_state.role == "Багш":
        menu = st.radio("ЦЭС", ["📊 Хянах самбар", "📝 Даалгавар өгөх", "📥 Ирсэн даалгавар", "🤖 AI Туслах"])
    else:
        menu = st.radio("ЦЭС", ["📚 Миний даалгавар", "📤 Даалгавар илгээх", "🤖 AI Туслах"])
    
    if st.button("🚪 Гарах"):
        st.session_state.auth = False
        st.rerun()

# --- БАГШИЙН ХЭСЭГ ---
if st.session_state.role == "Багш":
    if menu == "📝 Даалгавар өгөх":
        st.markdown("<h2 class='main-title'>Шинэ даалгавар үүсгэх</h2>", unsafe_allow_html=True)
        with st.form("hw_form"):
            subject = st.text_input("Хичээлийн нэр")
            title = st.text_input("Даалгаврын гарчиг")
            desc = st.text_area("Даалгаврын заавар")
            deadline = st.date_input("Дуусах хугацаа")
            if st.form_submit_button("Нийтлэх"):
                new_hw = {"id": len(st.session_state.homeworks)+1, "teacher": st.session_state.user, 
                          "subject": subject, "title": title, "desc": desc, "deadline": str(deadline)}
                st.session_state.homeworks.append(new_hw)
                st.success("✅ Даалгавар сурагчдад харагдахаар нийтлэгдлээ!")

    elif menu == "📥 Ирсэн даалгавар":
        st.markdown("<h2 class='main-title'>Сурагчдын илгээсэн бүтээлүүд</h2>", unsafe_allow_html=True)
        if not st.session_state.submissions:
            st.info("Одоогоор ирсэн даалгавар байхгүй байна.")
        for sub in st.session_state.submissions:
            with st.container():
                st.markdown(f"""<div class='card student-card'>
                    <h4>👤 {sub['student']} | 📚 {sub['hw_title']}</h4>
                    <p><b>Хариулт:</b> {sub['answer']}</p>
                    <small>Илгээсэн огноо: {sub['date']}</small>
                    </div>""", unsafe_allow_html=True)
                score = st.number_input(f"Оноо өгөх ({sub['student']})", 0, 100, key=f"score_{sub['date']}")
                if st.button(f"Дүн хадгалах {sub['student']}"):
                    st.success(f"{sub['student']}-д {score} оноо өглөө.")

# --- СУРАГЧИЙН ХЭСЭГ ---
elif st.session_state.role == "Сурагч":
    if menu == "📚 Миний даалгавар":
        st.markdown("<h2 class='main-title'>Өгөгдсөн даалгаврууд</h2>", unsafe_allow_html=True)
        if not st.session_state.homeworks:
            st.info("Багшаас өгсөн даалгавар байхгүй байна.")
        for hw in st.session_state.homeworks:
            st.markdown(f"""<div class='card'>
                <h3>📘 {hw['subject']}: {hw['title']}</h3>
                <p>{hw['desc']}</p>
                <p style='color:red;'>⏰ Дуусах хугацаа: {hw['deadline']}</p>
                <small>Багш: {hw['teacher']}</small>
                </div>""", unsafe_allow_html=True)

    elif menu == "📤 Даалгавар илгээх":
        st.markdown("<h2 class='main-title'>Даалгавар илгээх цонх</h2>", unsafe_allow_html=True)
        hw_to_submit = st.selectbox("Даалгавар сонгох", [hw['title'] for hw in st.session_state.homeworks])
        ans_text = st.text_area("Хариултаа энд бичнэ үү (эсвэл файл хавсаргана уу)")
        up_file = st.file_uploader("Файл хавсаргах", type=["pdf", "jpg", "png", "docx"])
        if st.button("Илгээх"):
            new_sub = {"student": st.session_state.user, "hw_title": hw_to_submit, 
                       "answer": ans_text, "date": str(datetime.datetime.now())}
            st.session_state.submissions.append(new_sub)
            st.success("🚀 Баяртай! Таны даалгавар багшид очлоо.")

# --- AI ТУСЛАХ (ХОЁР ТАЛД АЖИЛЛАНА) ---
if menu == "🤖 AI Туслах":
    st.markdown("<h2 class='main-title'>EduPlan AI Chat</h2>", unsafe_allow_html=True)
    if "chat_msgs" not in st.session_state: st.session_state.chat_msgs = []
    
    for m in st.session_state.chat_msgs:
        with st.chat_message(m["role"]): st.write(m["content"])
        
    if p := st.chat_input("Асуух зүйлээ бичнэ үү..."):
        st.session_state.chat_msgs.append({"role": "user", "content": p})
        with st.chat_message("user"): st.write(p)
        
        # AI Logic
        headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, 
                            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": p}]})
        if res.status_code == 200:
            ans = res.json()['choices'][0]['message']['content']
            with st.chat_message("assistant"): st.write(ans)
            st.session_state.chat_msgs.append({"role": "assistant", "content": ans})
