import streamlit as st
import requests
import datetime
from docx import Document
from io import BytesIO

# 1. Хуудасны тохиргоо (Орчин үеийн загвар)
st.set_page_config(
    page_title="Medle AI - Багшийн Туслах",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ашиглан дизайныг сайжруулах
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Статистик тоолох (Session State)
if 'plan_count' not in st.session_state:
    st.session_state.plan_count = 0
if 'teacher_list' not in st.session_state:
    st.session_state.teacher_list = set() # Давхардахгүйгээр багш нарыг тоолох

# 3. Нэвтрэх хэсэг (Validation)
def login_screen():
    st.sidebar.image("https://www.medle.mn/logo.png", width=150) # Medle лого (байвал)
    st.sidebar.title("🔐 Багшийн портал")
    email = st.sidebar.text_input("Албан ёсны эмайл (@medle.mn)", placeholder="нэр@medle.mn")
    password = st.sidebar.text_input("Нууц үг", type="password")
    
    if st.sidebar.button("Системд нэвтрэх"):
        if email.strip().lower().endswith("@medle.mn"):
            if len(password) > 0:
                st.session_state.logged_in = True
                st.session_state.user_email = email.strip().lower()
                st.session_state.teacher_list.add(email.strip().lower()) # Багшийг жагсаалтад нэмэх
                st.rerun()
            else:
                st.sidebar.error("Нууц үгээ оруулна уу.")
        else:
            st.sidebar.error("❌ Зөвхөн @medle.mn хаяг зөвшөөрөгдөнө!")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🎓 Medle.mn - Ухаалаг Багшийн Туслах")
    st.subheader("Ээлжит хичээлийн төлөвлөлтийн нэгдсэн систем")
    
    # Статистик харуулах хэсэг
    m1, m2 = st.columns(2)
    with m1:
        st.metric(label="📊 Нийт боловсруулсан төлөвлөгөө", value=st.session_state.plan_count)
    with m2:
        st.metric(label="👥 Идэвхтэй багш нарын тоо", value=len(st.session_state.teacher_list))
    
    st.info("💡 Үргэлжлүүлэхийн тулд зүүн талын цэсээр @medle.mn хаягаараа нэвтэрнэ үү.")
    login_screen()
    st.stop()

# 4. Үндсэн Программ (Нэвтэрсний дараа)
st.sidebar.success(f"👤 {st.session_state.user_email}")
if st.sidebar.button("Системээс гарах"):
    st.session_state.logged_in = False
    st.rerun()

# 5. Хичээл төлөвлөх хэсэг
st.title("📝 Ээлжит хичээлийн төлөвлөлт")

# Грокоос ирэх загварыг таны ирүүлсэн Excel бүтцээр тохируулсан
def generate_ai_plan(subject, grade, topic, duration):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
    
    prompt = f"""
    Монгол улсын 'ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ'-ийн албан ёсны загвараар боловсруул.
    Хичээл: {subject}, Анги: {grade}, Сэдэв: {topic}, Хугацаа: {duration} мин.
    
    Дараах бүтцээр гарга:
    1. Хичээлийн зорилго
    2. Үйл явцын хүснэгт (Эхлэл, Өрнөл, Төгсгөл үе шат бүрээр):
       - Хугацаа
       - Суралцахуйн үйл ажиллагаа
       - Багшийн дэмжлэг
       - Хэрэглэгдэхүүн
    3. Гэрийн даалгавар
    4. Ялгаатай сурагчидтай ажиллах аргачлал
    5. Багшийн дүгнэлт/Нэмэлт
    """
    
    data = {
        "model": "llama-3.3-70b-versatile", # Хамгийн сүүлийн үеийн загвар
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 200:
        st.session_state.plan_count += 1 # Төлөвлөгөөний тоог нэмэх
        return res.json()['choices'][0]['message']['content']
    return "AI холболтод алдаа гарлаа."

# Оролтын хэсэг
c1, c2 = st.columns(2)
with c1:
    sub = st.selectbox("📚 Хичээл", ["Мэдээлэл зүй", "Математик", "Физик", "Хими", "Англи хэл"])
    grd = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)])
with c2:
    tpc = st.text_input("🔍 Хичээлийн сэдэв", placeholder="Жишээ: Энгийн бутархай")
    dur = st.slider("⏱️ Хугацаа (мин)", 20, 90, 40)

if st.button("✨ Төлөвлөгөө боловсруулах"):
    if tpc:
        with st.spinner("AI таны ирүүлсэн загварын дагуу боловсруулж байна..."):
            result = generate_ai_plan(sub, grd, tpc, dur)
            st.success("Амжилттай боловсруулагдлаа!")
            st.markdown(result)
            
            # Word файл үүсгэх
            doc = Document()
            doc.add_heading(f"ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ - {tpc}", 0)
            doc.add_paragraph(result)
            bio = BytesIO()
            doc.save(bio)
            st.download_button("📥 Төлөвлөгөөг Word хэлбэрээр татах", bio.getvalue(), f"{tpc}.docx")
    else:
        st.warning("⚠️ Сэдвээ оруулна уу.")
