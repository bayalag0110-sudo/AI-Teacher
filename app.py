import streamlit as st
import requests
import datetime
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Medle AI - Багшийн Нэгдсэн Төв", layout="wide", page_icon="🎓")

# CSS - Орчин үеийн дизайн (Цэнхэр ба ногоон туяатай)
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 5px solid #28a745; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stSidebar { background-color: #f8f9fa; }
    .main-title { color: #1e3a8a; text-align: center; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Статистик (Session State ашиглан бодит тоолуур)
if 'plan_count' not in st.session_state:
    st.session_state.plan_count = 0
if 'teacher_emails' not in st.session_state:
    st.session_state.teacher_emails = set()

# 3. Нэвтрэх хэсэг (Зөвхөн @medle.mn)
def login():
    st.sidebar.title("🔐 Багшийн нэвтрэх")
    email = st.sidebar.text_input("Эмайл (@medle.mn)", placeholder="нэр@medle.mn")
    password = st.sidebar.text_input("Нууц үг", type="password")
    if st.sidebar.button("Системд нэвтрэх"):
        if email.strip().lower().endswith("@medle.mn") and password:
            st.session_state.logged_in = True
            st.session_state.user_email = email.strip().lower()
            st.session_state.teacher_emails.add(email.strip().lower())
            st.rerun()
        else:
            st.sidebar.error("❌ Зөвхөн @medle.mn хаягаар нэвтэрнэ!")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 class='main-title'>🎓 Medle AI - Багшийн Нэгдсэн Систем</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.metric("Нийт боловсруулсан төлөвлөгөө", st.session_state.plan_count)
    with c2: st.metric("Систем дэх багш нарын тоо", len(st.session_state.teacher_emails))
    login()
    st.stop()

# 4. Үндсэн цэс (Sidebar Navigation)
st.sidebar.success(f"👤 {st.session_state.user_email}")
menu = st.sidebar.selectbox("Үйлдэл сонгох", 
    ["📝 Ээлжит хичээл төлөвлөх", "📊 ESIS (bagsh.esis.edu.mn)", "👨‍🏫 Багшийн хөгжил (bagsh.edu.mn)", 
     "🗺️ EduMap.mn", "📚 Сурах бичиг (Econtent)", "🌐 Medle.mn"])

if st.sidebar.button("Гарах"):
    st.session_state.logged_in = False
    st.rerun()

# 5. Ээлжит хичээл төлөвлөх хэсэг
if menu == "📝 Ээлжит хичээл төлөвлөх":
    st.title("📝 Ээлжит хичээлийн төлөвлөлт")
    col1, col2 = st.columns([1, 1.3])
    
    with col1:
        st.subheader("⚙️ Хичээлийн мэдээлэл")
        sub = st.text_input("Хичээлийн нэр", "Мэдээлэл зүй")
        grd = st.selectbox("Анги", [f"{i}-р анги" for i in range(1, 13)])
        tpc = st.text_input("Ээлжит хичээлийн сэдэв", placeholder="Жишээ: Өгөгдлийн сан")
        dur = st.number_input("Хугацаа (минут)", 40)
        dt = st.date_input("Огноо", datetime.date.today())
        
        if st.button("✨ Төлөвлөгөө боловсруулах"):
            if tpc:
                with st.spinner("AI таны ирүүлсэн загварын дагуу боловсруулж байна..."):
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    # Загвар Excel-ийн дагуу зааварчилгаа
                    prompt = f"""
                    Монгол улсын ээлжит хичээлийн төлөвлөлтийн загвараар {sub} хичээлийн {grd}-ийн '{tpc}' сэдвээр төлөвлөгөө гарга.
                    БҮТЭЦ:
                    1. Хичээлийн зорилго
                    2. Үйл явц (Хүснэгтэн хэлбэрээр): Эхлэл, Өрнөл, Төгсгөл үе шатууд (Хугацаа, Суралцахуйн үйл ажиллагаа, Багшийн дэмжлэг, Хэрэглэгдэхүүн).
                    3. Гэрийн даалгавар
                    4. Ялгаатай сурагчидтай ажиллах аргачлал
                    5. Нэмэлт (Дүгнэлт)
                    """
                    res = requests.post(url, headers=headers, json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}]
                    })
                    if res.status_code == 200:
                        st.session_state.plan_count += 1
                        st.session_state.last_result = res.json()['choices'][0]['message']['content']
                    else:
                        st.error("AI холболтод алдаа гарлаа.")

    with col2:
        if 'last_result' in st.session_state:
            st.subheader("📄 Төлөвлөгөөний харагдац")
            st.markdown(st.session_state.last_result)
            
            # Word файл үүсгэх (БАТЛАВ хэсэгтэй)
            doc = Document()
            p = doc.add_paragraph("БАТЛАВ\nСУРГАЛТЫН МЕНЕЖЕР: .................")
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            doc.add_heading('ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph(f"Анги: {grd}\nСэдэв: {tpc}\nОгноо: {dt}\nХугацаа: {dur} минут")
            doc.add_paragraph(st.session_state.last_result)
            
            bio = BytesIO()
            doc.save(bio)
            st.download_button("📥 Word файл татах", bio.getvalue(), f"Plan_{tpc}.docx")

# 6. Вэб сайтуудыг нэгтгэх хэсэг (Iframe холболтууд)
elif menu == "📊 ESIS (bagsh.esis.edu.mn)":
    st.title("📊 Боловсролын салбарын мэдээллийн систем")
    st.components.v1.iframe("https://bagsh.esis.edu.mn/", height=800, scrolling=True)

elif menu == "👨‍🏫 Багшийн хөгжил (bagsh.edu.mn)":
    st.title("👨‍🏫 Багшийн хөгжлийн нэгдсэн портал")
    st.components.v1.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)

elif menu == "🗺️ EduMap.mn":
    st.title("🗺️ EduMap - Сургалтын хөтөлбөрийн сан")
    st.components.v1.iframe("https://edumap.mn/", height=800, scrolling=True)

elif menu == "📚 Сурах бичиг (Econtent)":
    st.title("📚 Цахим сурах бичгийн сан")
    st.components.v1.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)

elif menu == "🌐 Medle.mn":
    st.title("🌐 Medle Цахим сургууль")
    st.components.v1.iframe("https://medle.mn/", height=800, scrolling=True)
