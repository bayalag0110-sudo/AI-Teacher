import streamlit as st
import requests
import datetime
from docx import Document
from io import BytesIO

# 1. Хуудасны тохиргоо болон Статистик
st.set_page_config(page_title="Medle.mn Багшийн Туслах", layout="wide")

if 'total_plans' not in st.session_state:
    st.session_state.total_plans = 150  # Жишээ статистик
if 'total_teachers' not in st.session_state:
    st.session_state.total_teachers = 82 # Жишээ статистик

# 2. Нэвтрэх хэсэг (Зөвхөн medle.mn)
def login():
    st.sidebar.title("🔐 Багшийн нэвтрэх")
    email = st.sidebar.text_input("Эмайл хаяг (Жишээ: name@medle.mn)")
    password = st.sidebar.text_input("Нууц үг", type="password")
    
    if st.sidebar.button("Нэвтрэх"):
        if email.endswith("@medle.mn"):
            if password: # Бодит системд нууц үгийг шалгана
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.sidebar.error("Нууц үгээ оруулна уу.")
        else:
            st.sidebar.error("Зөвхөн @medle.mn хаягаар нэвтрэх боломжтой!")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🎓 Ухаалаг Багшийн Туслах (Medle.mn)")
    st.warning("⚠️ Энэхүү системд зөвхөн @medle.mn албан ёсны эмайл хаягаар нэвтэрнэ.")
    
    # Статистик харуулах
    col1, col2 = st.columns(2)
    col1.metric("Нийт боловсруулсан хичээл", st.session_state.total_plans)
    col2.metric("Нийт идэвхтэй багш нар", st.session_state.total_teachers)
    login()
    st.stop()

# 3. Үндсэн Программ (Нэвтэрсний дараа)
st.sidebar.success(f"Нэвтэрсэн: {st.session_state.user_email}")
if st.sidebar.button("Гарах"):
    st.session_state.logged_in = False
    st.rerun()

st.title("📝 Ээлжит хичээлийн төлөвлөлт")

# 4. AI холболт (Llama 3.3)
def generate_plan(subject, grade, topic, duration):
    if "GROQ_API_KEY" not in st.secrets:
        return "API Key тохируулаагүй байна."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}", "Content-Type": "application/json"}
    
    # Таны ирүүлсэн Excel загварын дагуу Prompt
    prompt = f"""
    Чи бол Монгол улсын багш. Дараах 'ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ'-ийг боловсруул.
    Хичээл: {subject}, Анги: {grade}, Сэдэв: {topic}, Хугацаа: {duration} мин.
    
    Бүтэц (Заавал):
    1. Хичээлийн зорилго
    2. Үйл явц (Хүснэгт):
       - Эхлэл хэсэг (сэдэлжүүлэг, сэргээн санах)
       - Өрнөл хэсэг (мэдлэг бүтээх)
       - Төгсгөл хэсэг (дүгнэлт, үнэлгээ)
    3. Гэрийн даалгавар
    4. Ялгаатай сурагчидтай ажиллах аргачлал
    5. Багшийн дүгнэлт /Нэмэлт/
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        res = requests.post(url, headers=headers, json=data, timeout=30)
        if res.status_code == 200:
            st.session_state.total_plans += 1
            return res.json()['choices'][0]['message']['content']
        return f"Алдаа: {res.text}"
    except Exception as e:
        return f"Холболтын алдаа: {str(e)}"

# 5. Хэрэглэгчийн интерфейс
col_a, col_b = st.columns(2)
with col_a:
    sub = st.text_input("Хичээлийн нэр", "Мэдээлэл зүй")
    grd = st.selectbox("Анги", [f"{i}-р анги" for i in range(1, 13)])
with col_b:
    tpc = st.text_input("Хичээлийн сэдэв")
    dur = st.number_input("Хугацаа (минут)", value=40)

if st.button("✨ Төлөвлөгөө боловсруулах"):
    if tpc:
        with st.spinner("AI боловсруулж байна..."):
            result = generate_plan(sub, grd, tpc, dur)
            st.markdown(result)
            
            # Word файл татах
            doc = Document()
            doc.add_heading("ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ", 0)
            doc.add_paragraph(result)
            bio = BytesIO()
            doc.save(bio)
            st.download_button("📥 Word татах", bio.getvalue(), f"{tpc}.docx")
