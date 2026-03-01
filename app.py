import streamlit as st
import requests
import datetime
import PyPDF2
from docx import Document
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Medle AI - Ухаалаг Багш", layout="wide", page_icon="🎓")

# CSS - Орчин үеийн загвар
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 5px solid #007bff; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Статистик (Session State)
if 'plan_count' not in st.session_state: st.session_state.plan_count = 0
if 'teacher_emails' not in st.session_state: st.session_state.teacher_emails = set()

# 3. Нэвтрэх хэсэг
def login():
    st.sidebar.title("🔐 Багшийн нэвтрэх")
    email = st.sidebar.text_input("Эмайл (@medle.mn)")
    password = st.sidebar.text_input("Нууц үг", type="password")
    if st.sidebar.button("Нэвтрэх"):
        if email.strip().lower().endswith("@medle.mn") and password:
            st.session_state.logged_in = True
            st.session_state.user_email = email.strip().lower()
            st.session_state.teacher_emails.add(email.strip().lower())
            st.rerun()
        else:
            st.sidebar.error("❌ Зөвхөн @medle.mn хаяг зөвшөөрөгдөнө!")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🎓 Medle AI - Багшийн Нэгдсэн Систем")
    c1, c2 = st.columns(2)
    c1.metric("Нийт боловсруулсан материал", st.session_state.plan_count)
    c2.metric("Систем дэх багш нар", len(st.session_state.teacher_emails))
    login()
    st.stop()

# 4. Үндсэн цэс
st.sidebar.success(f"👤 {st.session_state.user_email}")
menu = st.sidebar.selectbox("Цэс сонгох", 
    ["📖 Сурах бичгээс бэлтгэх", "📝 Ээлжит хичээл (Шинэ)", "📊 ESIS", "🗺️ EduMap", "🌐 Medle.mn"])

if st.sidebar.button("Гарах"):
    st.session_state.logged_in = False
    st.rerun()

# 5. ШИНЭ ФУНКЦ: СУРАХ БИЧГЭЭС БОЛОВСРУУЛАХ
if menu == "📖 Сурах бичгээс бэлтгэх":
    st.title("📖 Сурах бичгээс материал бэлтгэх")
    st.info("Сурах бичгийнхээ PDF файлыг оруулснаар AI түүн дээр үндэслэн төлөвлөгөө болон сорил бэлдэнэ.")
    
    uploaded_file = st.file_uploader("Сурах бичгийн хуудсыг PDF хэлбэрээр оруулна уу", type="pdf")
    
    if uploaded_file is not None:
        # PDF-ээс текст унших
        reader = PyPDF2.PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text()
        
        st.success("✅ Сурах бичгийн текстийг амжилттай уншлаа.")
        
        tab1, tab2 = st.tabs(["📋 Ээлжит хичээл бэлтгэх", "⏱️ 5 минутын сорил бэлдэх"])
        
        with tab1:
            if st.button("✨ Төлөвлөгөө үүсгэх"):
                with st.spinner("AI текстийг шинжилж байна..."):
                    prompt = f"Дараах сурах бичгийн эх бичвэр дээр үндэслэн ээлжит хичээлийн төлөвлөгөөг (Эхлэл, Өрнөл, Төгсгөл) боловсруулж өг: {full_text[:2000]}"
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    res = requests.post(url, headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    if res.status_code == 200:
                        st.session_state.plan_count += 1
                        st.markdown(res.json()['choices'][0]['message']['content'])
        
        with tab2:
            num_questions = st.slider("Асуултын тоо", 3, 10, 5)
            if st.button("⏱️ Сорил бэлдэх"):
                with st.spinner("5 минутын сорил бэлтгэж байна..."):
                    prompt = f"Дараах эх бичвэр дээр үндэслэн сурагчдын мэдлэгийг шалгах {num_questions} асуулт бүхий '5 минутын сорил' бэлд. Асуулт бүр 4 сонголттой, зөв хариулттай байх ёстой: {full_text[:2000]}"
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    res = requests.post(url, headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    if res.status_code == 200:
                        st.session_state.plan_count += 1
                        st.session_state.quiz_result = res.json()['choices'][0]['message']['content']
                        st.markdown(st.session_state.quiz_result)
                        
                        # Word татах
                        doc = Document()
                        doc.add_heading('5 МИНУТЫН СОРИЛ', 0)
                        doc.add_paragraph(st.session_state.quiz_result)
                        bio = BytesIO()
                        doc.save(bio)
                        st.download_button("📥 Сорилыг Word-оор татах", bio.getvalue(), "Quiz.docx")

# Бусад цэсүүд (Өмнөх кодын дагуу)
elif menu == "📝 Ээлжит хичээл (Шинэ)":
    st.title("📝 Ээлжит хичээлийн төлөвлөлт")
    # ... (Өмнөх төлөвлөгөөний код энд орно)

elif menu == "📊 ESIS":
    st.components.v1.iframe("https://bagsh.esis.edu.mn/", height=800)
