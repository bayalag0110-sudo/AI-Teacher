import streamlit as st
import requests
import datetime
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# 1. Хуудасны тохиргоо ба Дизайн
st.set_page_config(page_title="Medle AI - Ээлжит хичээл", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    .main-title { color: #1E3A8A; font-size: 30px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. Статистик (Session State)
if 'plan_count' not in st.session_state:
    st.session_state.plan_count = 0
if 'teacher_emails' not in st.session_state:
    st.session_state.teacher_emails = set()

# 3. Нэвтрэх хэсэг
def login():
    st.sidebar.title("🔐 Нэвтрэх")
    email = st.sidebar.text_input("Эмайл (@medle.mn)")
    password = st.sidebar.text_input("Нууц үг", type="password")
    if st.sidebar.button("Нэвтрэх"):
        if email.strip().lower().endswith("@medle.mn") and password:
            st.session_state.logged_in = True
            st.session_state.user_email = email.strip().lower()
            st.session_state.teacher_emails.add(email.strip().lower())
            st.rerun()
        else:
            st.sidebar.error("Зөвхөн @medle.mn хаягаар нэвтэрнэ!")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🎓 Ухаалаг Багшийн Туслах Систем</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Нийт боловсруулсан хичээл", st.session_state.plan_count)
    c2.metric("Бүртгэлтэй багш нар", len(st.session_state.teacher_emails))
    login()
    st.stop()

# 4. Үндсэн Программ
st.sidebar.success(f"👤 {st.session_state.user_email}")
if st.sidebar.button("Гарах"):
    st.session_state.logged_in = False
    st.rerun()

st.title("📝 Ээлжит хичээлийн төлөвлөлт")

# 5. Groq AI Функц (Таны загварын дагуу)
def generate_eeljit_plan(subject, grade, topic, duration, date):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
    
    # Загвар файлаас авсан бүтэц
    prompt = f"""
    Чи бол Монгол улсын багш. Дараах 'ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ'-ийг яг энэ бүтцээр гарга:
    Хичээл: {subject}, Анги: {grade}, Сэдэв: {topic}, Огноо: {date}, Хугацаа: {duration} мин.

    БҮТЭЦ:
    - Хичээлийн зорилго:
    - Үйл явцын хүснэгт:
      1. Эхлэл хэсэг (зорилго тодорхойлох, сэдэлжүүлэг, сэргээн санах): Хугацаа, Суралцахуйн үйл ажиллагаа, Багшийн дэмжлэг, Хэрэглэгдэхүүн.
      2. Өрнөл хэсэг (арга, мэдээлэл боловсруулах, задлан шинжлэх, мэдлэг бүтээх): Хугацаа, Суралцахуйн үйл ажиллагаа, Багшийн дэмжлэг, Хэрэглэгдэхүүн.
      3. Төгсгөл хэсэг (ойлголтоо нэгтгэн дүгнэх, үнэлгээ): Хугацаа, Суралцахуйн үйл ажиллагаа, Багшийн дэмжлэг, Хэрэглэгдэхүүн.
    - Гэрийн даалгавар:
    - Ялгаатай сурагчидтай ажиллах аргачлал:
    - Нэмэлт (Дүгнэлт, сайжруулах санаа):
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200:
        st.session_state.plan_count += 1
        return res.json()['choices'][0]['message']['content']
    return "Алдаа гарлаа."

# 6. Оролт ба Гаралт
col1, col2 = st.columns(2)
with col1:
    sub = st.text_input("Хичээлийн нэр", "Мэдээлэл зүй")
    grd = st.selectbox("Анги", [f"{i}-р анги" for i in range(1, 13)])
with col2:
    tpc = st.text_input("Ээлжит хичээлийн сэдэв")
    dur = st.number_input("Хугацаа (минут)", 40)
    dt = st.date_input("Огноо", datetime.date.today())

if st.button("✨ Төлөвлөгөө боловсруулах"):
    if tpc:
        with st.spinner("Таны ирүүлсэн загварын дагуу боловсруулж байна..."):
            result = generate_eeljit_plan(sub, grd, tpc, dur, dt)
            st.markdown("### 📄 Боловсруулсан төлөвлөгөө")
            st.write(result)
            
            # Word файл (Загварын дагуу БАТЛАВ хэсэгтэй)
            doc = Document()
            p = doc.add_paragraph("БАТЛАВ\nСУРГАЛТЫН МЕНЕЖЕР: .................")
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            doc.add_heading('ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph(f"Анги: {grd}\nСар, өдөр, хугацаа: {dt}, {dur} мин\nСэдэв: {tpc}")
            doc.add_paragraph(result)
            
            bio = BytesIO()
            doc.save(bio)
            st.download_button("📥 Word хэлбэрээр татах", bio.getvalue(), f"{tpc}.docx")
    else:
        st.warning("Сэдвээ оруулна уу.")
