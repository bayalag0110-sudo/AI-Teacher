import streamlit as st
import requests
import datetime
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Medle AI - Багшийн Төв", layout="wide", page_icon="🎓")

# CSS - Порталуудыг харуулах болон дизайны тохиргоо
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 5px; padding: 10px; }
    iframe { border-radius: 10px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# 2. Түүх болон Статистик
if 'history' not in st.session_state: st.session_state.history = []
if 'teacher_emails' not in st.session_state: st.session_state.teacher_emails = set()

# 3. Нэвтрэх хэсэг
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

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
            st.sidebar.error("❌ Зөвхөн @medle.mn хаяг!")

if not st.session_state.logged_in:
    st.title("🎓 Medle AI - Ухаалаг Багшийн Систем")
    login()
    st.stop()

# 4. Sidebar - Түүх харуулах
st.sidebar.success(f"👤 {st.session_state.user_email}")
with st.sidebar.expander("🕒 Боловсруулсан түүх"):
    for item in st.session_state.history:
        st.caption(f"{item['date']} - {item['topic']}")

if st.sidebar.button("Гарах"):
    st.session_state.logged_in = False
    st.rerun()

# 5. ҮНДСЭН ХЭСЭГ: ПОРТАЛУУД БА ХИЧЭЭЛ ТӨЛӨВЛӨЛТ
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Хичээл төлөвлөх (Econtent-той)", 
    "📊 ESIS", "🗺️ EduMap", "👨‍🏫 Багшийн хөгжил", "💻 Medle.mn"
])

# --- TAB 1: ECONTENT БОЛОН ХИЧЭЭЛ ТӨЛӨВЛӨЛТ ---
with tab1:
    col_book, col_plan = st.columns([1.2, 1])
    
    with col_book:
        st.subheader("📚 Сурах бичиг харах")
        book_url = st.text_input("Econtent номын линк:", "https://econtent.edu.mn/book/12bek/1")
        # Номыг вэб дотор харуулах
        st.components.v1.iframe(book_url, height=700, scrolling=True)
    
    with col_plan:
        st.subheader("⚙️ Төлөвлөгөө боловсруулах")
        page_range = st.text_input("Ашиглах хуудас (Жишээ: 12-15):")
        topic = st.text_input("Хичээлийн сэдэв:")
        
        if st.button("✨ AI-аар боловсруулах"):
            if topic and page_range:
                with st.spinner("Номын агуулгыг шинжилж байна..."):
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    
                    # Таны загвар файлын дагуу Prompt
                    prompt = f"""
                    Чи бол Монгол улсын багш. '{book_url}' номын {page_range}-р хуудсанд байгаа агуулгын хүрээнд '{topic}' сэдэвтэй ээлжит хичээлийг боловсруул.
                    БҮТЭЦ (Заавал):
                    1. Хичээлийн зорилго
                    2. Үйл явцын хүснэгт (Хугацаа, Суралцахуйн үйл ажиллагаа, Багшийн дэмжлэг, Хэрэглэгдэхүүн баганатай):
                       - Эхлэл хэсэг
                       - Өрнөл хэсэг
                       - Төгсгөл хэсэг
                    3. Гэрийн даалгавар
                    4. Ялгаатай сурагчидтай ажиллах аргачлал
                    5. Багшийн дүгнэлт (Нэмэлт)
                    """
                    
                    res = requests.post(url, headers=headers, json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}]
                    })
                    
                    if res.status_code == 200:
                        ans = res.json()['choices'][0]['message']['content']
                        st.session_state.history.append({"date": str(datetime.date.today()), "topic": topic, "content": ans})
                        st.markdown(ans)
                        
                        # Word татах
                        doc = Document()
                        doc.add_heading('ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ', 0)
                        doc.add_paragraph(ans)
                        bio = BytesIO()
                        doc.save(bio)
                        st.download_button("📥 Word татах", bio.getvalue(), f"{topic}.docx")
            else:
                st.warning("⚠️ Сэдэв болон хуудсаа оруулна уу.")

# --- БУСАД ПОРТАЛУУДЫГ IFRAME-ЭЭР ХАРУУЛАХ ---
with tab2:
    st.components.v1.iframe("https://bagsh.esis.edu.mn/", height=800, scrolling=True)

with tab3:
    st.components.v1.iframe("https://edumap.mn/", height=800, scrolling=True)

with tab4:
    st.components.v1.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)

with tab5:
    st.components.v1.iframe("https://medle.mn/", height=800, scrolling=True)
