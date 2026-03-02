import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v5.9", layout="wide", page_icon="🎓")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); }
    .glass-card {
        background: white !important;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    label, p, h1, h2, h3 { color: #1e293b !important; }
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        font-weight: 700;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ТУСЛАХ ФУНКЦҮҮД ---
def extract_pdf_text(file, start, end):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for i in range(start-1, min(end, len(reader.pages))):
            text += reader.pages[i].extract_text()
        return text
    except: return ""

def create_word_doc(content):
    doc = Document()
    doc.add_heading('Ээлжит хичээлийн төлөвлөгөө', 0)
    doc.add_paragraph(content)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- НЭВТРЭХ ХЭСЭГ (Товчилсон) ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        st.image('450633998_2213051369057631_4561852154062620515_n.jpg', width=150)
        st.title("EduPlan Pro")
        u_pwd = st.text_input("Нууц үг", type="password")
        if st.button("Нэвтрэх"):
            if u_pwd == "admin1234": st.session_state.auth = True; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    menu = st.radio("ЦЭС", ["💎 Ээлжит төлөвлөгч", "🤖 AI Чатбот", "🌍 Портал"])

# --- 💎 ЭЭЛЖИТ ТӨЛӨВЛӨГЧ (ШИНЭЧЛЭГДСЭН ЛОГИК) ---
if menu == "💎 Ээлжит төлөвлөгч":
    st.title("💎 Ухаалаг хичээл төлөвлөлт")
    col1, col2 = st.columns([1, 1.8])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        p_file = st.file_uploader("Сурах бичиг (PDF)", type="pdf")
        p_start = st.number_input("Эхлэх хуудас", 1, value=1)
        p_end = st.number_input("Дуусах хуудас", 1, value=2)
        p_subject = st.text_input("Хичээл", value="Мэдээллийн технологи")
        p_grade = st.text_input("Анги", value="9-р анги")
        p_topic = st.text_input("Сэдэв", value="Өгөгдлийн шинж чанараар эрэмбэлэх, шүүлт хийх")
        
        if st.button("🚀 Төлөвлөгөө боловсруулах"):
            if p_topic:
                with st.spinner("Таны заасан промтын дагуу боловсруулж байна..."):
                    pdf_context = extract_pdf_text(p_file, p_start, p_end) if p_file else ""
                    
                    # ТАНЫ ӨГСӨН ТУСГАЙ ПРОМТ
                    prompt = f"""
                    Чи бол Монгол улсын ЕБС-ийн мэргэжлийн багш. Дараах зааврын дагуу хичээлийн төлөвлөгөөг ХҮСНЭГТЭН хэлбэрээр гарга:
                    
                    Хичээл: {p_subject}, Анги: {p_grade}, Сэдэв: {p_topic}
                    Эх сурвалж агуулга: {pdf_context[:2000]}
                    
                    БҮТЭЦ:
                    1. Суралцахуйн зорилт: Bloom taxonomy-ийн дагуу тодорхойлох.
                    2. Хичээлийн үе шат: Танилцуулга, Үндсэн агуулга, Дүгнэлт бэхжилт гэсэн бүтэцтэй.
                    3. Арга зүй: Сурагчийн оролцоог нэмэгдүүлэх бүлгийн болон ганцаарчилсан ажлуудыг тусгах.
                    4. 3 Түвшний даалгавар:
                       - Түвшин 1 (Дутуу эзэмшсэн): Үндсэн ойлголт, нэр томьёо таних.
                       - Түвшин 2 (Эзэмшиж буй): Жишээ, асуулттай ажиллах.
                       - Түвшин 3 (Бүрэн эзэмшсэн): Чадвар шаардсан бүтээлч бодлого.
                    5. Үнэлгээ: 5 минутын асуулт, даалгавар оруулах.
                    
                    Хариуг маш цэвэрхэн Markdown хүснэгт ашиглан Монгол хэлээр гарга.
                    """
                    
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    st.session_state.final_plan = res.json()['choices'][0]['message']['content']
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if 'final_plan' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.final_plan)
            st.download_button("📥 Word файл татах", create_word_doc(st.session_state.final_plan), "Lesson_Plan.docx")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 🌍 ПОРТАЛ ---
elif menu == "🌍 Портал":
    st.title("🌍 Боловсролын Порталууд")
    t = st.tabs(["📚 E-Content", "👨‍🏫 Bagsh.edu.mn", "📊 EEC"])
    with t[0]: components.iframe("https://econtent.edu.mn/book", height=800)
    with t[1]: components.iframe("https://bagsh.edu.mn/", height=800)
    with t[2]: components.iframe("https://www.eec.mn/", height=800)
