import streamlit as st
import requests
import datetime
from docx import Document
from io import BytesIO

# 1. Хуудасны тохиргоо болон Статистик (Session State ашиглав)
st.set_page_config(page_title="Багшийн Туслах", layout="wide")

if 'total_plans' not in st.session_state:
    st.session_state.total_plans = 124  # Жишээ статистик
if 'total_teachers' not in st.session_state:
    st.session_state.total_teachers = 45 # Жишээ статистик

# 2. Нэвтрэх хэсэг (Login)
def login():
    st.sidebar.title("🔐 Нэвтрэх")
    email = st.sidebar.text_input("Эмайл хаяг")
    password = st.sidebar.text_input("Нууц үг", type="password")
    if st.sidebar.button("Нэвтрэх"):
        if email and password: # Бодит системд энд баазтай тулгана
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.rerun()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🎓 Ухаалаг Багшийн Туслах Систем")
    st.info("Үргэлжлүүлэхийн тулд зүүн талын цэсээр нэвтэрнэ үү.")
    
    # Статистик харуулах (Нэвтрээгүй үед ч харагдана)
    col1, col2 = st.columns(2)
    col1.metric("Нийт боловсруулсан хичээл", st.session_state.total_plans)
    col2.metric("Нийт бүртгэлтэй багш нар", st.session_state.total_teachers)
    login()
    st.stop()

# 3. Үндсэн Программ (Нэвтэрсний дараа)
st.sidebar.success(f"Нэвтэрсэн: {st.session_state.user_email}")
if st.sidebar.button("Гарах"):
    st.session_state.logged_in = False
    st.rerun()

st.title("📝 Ээлжит хичээлийн төлөвлөлт")

# 4. Groq AI функц (Llama 3.3 ашиглав)
def generate_plan(subject, grade, topic, duration):
    if "GROQ_API_KEY" not in st.secrets:
        return "API Key тохируулаагүй байна."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}", "Content-Type": "application/json"}
    
    # Таны ирүүлсэн Excel загварын дагуу Prompt
    prompt = f"""
    Монгол улсын 'ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ'-ийн загварын дагуу боловсруул.
    Хичээл: {subject}, Анги: {grade}, Сэдэв: {topic}, Хугацаа: {duration} мин.
    
    Бүтэц:
    1. Хичээлийн зорилго
    2. Үйл явц (Хүснэгт):
       - Эхлэл хэсэг (сэдэлжүүлэг, сэргээн санах)
       - Өрнөл хэсэг (мэдлэг бүтээх)
       - Төгсгөл хэсэг (дүгнэлт, үнэлгээ)
    3. Гэрийн даалгавар
    4. Ялгаатай сурагчидтай ажиллах аргачлал
    5. Багшийн дүгнэлт
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 200:
        st.session_state.total_plans += 1 # Статистик нэмэх
        return res.json()['choices'][0]['message']['content']
    return f"Алдаа: {res.text}"

# 5. Интерфэйс
col_a, col_b = st.columns(2)
with col_a:
    sub = st.text_input("Хичээл", "Мэдээлэл зүй")
    grd = st.selectbox("Анги", [f"{i}-р анги" for i in range(1, 13)])
with col_b:
    tpc = st.text_input("Хичээлийн сэдэв")
    dur = st.number_input("Хугацаа (мин)", value=40)

if st.button("Төлөвлөгөө боловсруулах"):
    if tpc:
        with st.spinner("AI ажиллаж байна..."):
            result = generate_plan(sub, grd, tpc, dur)
            st.markdown(result)
            
            # Word файл татах
            doc = Document()
            doc.add_heading("ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ", 0)
            doc.add_paragraph(result)
            bio = BytesIO()
            doc.save(bio)
            st.download_button("📥 Word татах", bio.getvalue(), f"{tpc}.docx")
