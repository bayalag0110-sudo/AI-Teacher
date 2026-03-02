import streamlit as st
import requests
import datetime
import PyPDF2
from docx import Document
from io import BytesIO

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v4.4", layout="wide", page_icon="🎓")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .glass-card { background: white; border-radius: 15px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .main-title { text-align: center; font-weight: 800; background: linear-gradient(90deg, #2563eb, #9333ea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .teacher-header { background: linear-gradient(90deg, #1e3a8a, #3b82f6); padding: 15px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN LOGIC (ШИНЭЧЛЭГДСЭН) ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='margin-top:80px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1 class='main-title'>EduPlan Pro</h1>", unsafe_allow_html=True)
        
        u_role = st.radio("Та хэн бэ?", ["Багш", "Сурагч"], horizontal=True)
        u_name = st.text_input("Нэр:")
        
        # Зөвхөн Сурагч нэвтрэхэд АНГИ харуулна
        u_class = ""
        if u_role == "Сурагч":
            u_class = st.text_input("Анги / Бүлэг (Жишээ нь: 10А):").upper()
            
        u_pwd = st.text_input("Нууц үг:", type="password")
        
        if st.button("Нэвтрэх"):
            if u_pwd == "admin1234" and u_name:
                if u_role == "Сурагч" and not u_class:
                    st.error("Ангиа оруулна уу!")
                else:
                    st.session_state.auth = True
                    st.session_state.role = u_role
                    st.session_state.user = u_name
                    st.session_state.u_class = u_class # Багш бол хоосон байна
                    st.rerun()
            else:
                st.error("Нэр эсвэл нууц үг буруу байна!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user}")
    st.caption(f"📍 {st.session_state.role} " + (f"| 🏫 {st.session_state.u_class}" if st.session_state.u_class else ""))
    st.divider()
    
    if st.session_state.role == "Багш":
        menu = st.radio("ЦЭС", ["💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📝 Даалгавар өгөх", "🤖 AI Чатбот", "🌍 Портал"])
    else:
        menu = st.radio("ЦЭС", ["📚 Миний даалгавар", "📤 Даалгавар илгээх", "🤖 AI Туслах"])
        
    if st.button("🚪 Гарах"):
        st.session_state.auth = False
        st.rerun()

# --- БАГШИЙН ХЭСЭГ: ДААЛГАВАР ӨГӨХ ---
if st.session_state.role == "Багш" and menu == "📝 Даалгавар өгөх":
    st.markdown("<div class='teacher-header'><h1>📝 Даалгавар нийтлэх</h1></div>", unsafe_allow_html=True)
    with st.form("hw_form"):
        target_class = st.text_input("Аль ангид өгөх вэ? (Жишээ нь: 10А, 10Б...)", placeholder="10А")
        hw_title = st.text_input("Даалгаврын гарчиг")
        hw_desc = st.text_area("Зааварчилгаа")
        hw_deadline = st.date_input("Дуусах хугацаа")
        if st.form_submit_button("🚀 Нийтлэх"):
            if target_class and hw_title:
                st.success(f"✅ {target_class} ангийн сурагчдад '{hw_title}' даалгавар амжилттай илгээгдлээ.")
            else:
                st.warning("Анги болон гарчгийг бөглөнө үү!")

# (Ээлжит төлөвлөгч, Тест үүсгэгч болон бусад кодууд өмнөх хэвээр үргэлжилнэ...)
