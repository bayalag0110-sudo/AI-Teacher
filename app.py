import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2
from PIL import Image

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v6.2", layout="wide", page_icon="🎓")

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
    label, p, h1, h2, h3, span { color: #1e293b !important; font-weight: 500; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        font-weight: 700;
        border-radius: 10px;
        border: none;
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

def extract_docx_text(file):
    try:
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    except: return ""

def create_word_doc(content, title):
    doc = Document()
    doc.add_heading(title, 0)
    doc.add_paragraph(content)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- НЭВТРЭХ ХЭСЭГ ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div class="glass-card" style="text-align:center; margin-top:50px;">', unsafe_allow_html=True)
        try: st.image('450633998_2213051369057631_4561852154062620515_n.jpg', width=180)
        except: st.title("🎓 EduPlan")
        u_name = st.text_input("👤 Хэрэглэгчийн нэр")
        u_pwd = st.text_input("🔑 Нууц үг", type="password")
        if st.button("НЭВТРЭХ"):
            if u_pwd == "admin1234": st.session_state.auth, st.session_state.user = True, u_name; st.rerun()
    st.stop()

# --- SIDEBAR МЕНЮ ---
with st.sidebar:
    st.markdown(f"### 👋 Сайн уу, {st.session_state.user}")
    menu = st.radio("ҮНДСЭН ЦЭС", ["💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📝 Даалгавар өгөх", "🤖 AI Чатбот", "🌍 Портал"])
    if st.button("🚪 Гарах"): st.session_state.auth = False; st.rerun()

# --- 1. 💎 ЭЭЛЖИТ ТӨЛӨВЛӨГЧ (Сайжруулсан загвар) ---
if menu == "💎 Ээлжит төлөвлөгч":
    st.title("💎 Ухаалаг хичээл төлөвлөлт")
    col1, col2 = st.columns([1, 1.8])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        p_file = st.file_uploader("Сурах бичиг хавсаргах (PDF)", type="pdf")
        p_start = st.number_input("Эхлэх хуудас", 1, value=1)
        p_end = st.number_input("Дуусах хуудас", 1, value=2)
        subj = st.text_input("Хичээл", value="Мэдээллийн технологи")
        grade = st.text_input("Анги", value="9-р анги")
        topic = st.text_input("Сэдэв", placeholder="Сэдвээ бичнэ үү...")
        
        if st.button("🚀 Төлөвлөгөө боловсруулах"):
            if topic:
                with st.spinner("AI таны заасан загварын дагуу төлөвлөж байна..."):
                    pdf_context = extract_pdf_text(p_file, p_start, p_end) if p_file else ""
                    
                    instruction = f"""
                    Чи бол Монгол улсын ЕБС-ийн мэргэжлийн багш. Төлөвлөгөөг ХҮСНЭГТЭН хэлбэрээр дараах бүтцээр гарга:
                    
                    Хичээл: {subj}, Анги: {grade}, Сэдэв: {topic}
                    Сурах бичгийн агуулга: {pdf_context[:2000]}
                    
                    ШААРДЛАГА:
                    1. Суралцахуйн зорилт: Bloom taxonomy-ийн дагуу (Санах, Ойлгох, Хэрэглэх, Шинжлэх, Үнэлэх, Бүтээх).
                    2. Үйл явцын хүснэгт (БАГАНУУД: Үе шат, Хугацаа, Суралцахуйн үйл ажиллагаа, Багшийн дэмжлэг, Хэрэглэгдэхүүн):
                       - Эхлэл хэсэг (Зорилго, Сэдэлжүүлэг)
                       - Өрнөл хэсэг (Арга зүй, Мэдлэг бүтээх, Бүлгийн болон ганцаарчилсан ажил)
                       - Төгсгөл хэсэг (Дүгнэлт, Багцлах, 5 минутын асуулт/даалгавар)
                    3. Дасгал, даалгавар (3 түвшинд):
                       - Бүрэн эзэмшсэн сурагчид (Түвшин 3): Чадвар шаардсан бүтээлч бодлого.
                       - Эзэмшиж буй сурагчид (Түвшин 2): Жишээ, асуулттай ажиллах.
                       - Дутуу эзэмшсэн сурагчид (Түвшин 1): Үндсэн ойлголт, нэр томьёо таних.
                    4. Гэрийн даалгавар ба Ялгаатай сурагчидтай ажиллах аргачлал.
                    """
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": instruction}]})
                    st.session_state.plan_result = res.json()['choices'][0]['message']['content']
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'plan_result' in st.session_state:
            st.markdown(f'<div class="glass-card">{st.session_state.plan_result}</div>', unsafe_allow_html=True)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.plan_result, topic), f"{topic}_plan.docx")

# --- 2. 🤖 AI ЧАТБОТ (PDF, Excel, Word, Зураг) ---
elif menu == "🤖 AI Чатбот":
    st.title("🤖 AI Ухаалаг туслах")
    with st.expander("📎 Файл хавсаргах (PDF, Word, Excel, Зураг)"):
        up = st.file_uploader("Файл сонгох", type=['pdf', 'docx', 'xlsx', 'jpg', 'png'])
        context = ""
        if up:
            if up.name.endswith('.pdf'): context = extract_pdf_text(up, 1, 5)
            elif up.name.endswith('.docx'): context = extract_docx_text(up)
            elif up.name.endswith('.xlsx'):
                df = pd.read_excel(up, engine='openpyxl')
                context = df.to_string(); st.dataframe(df.head())
            else: st.image(up, width=200); context = "[Зураг хавсаргав]"

    if "msgs" not in st.session_state: st.session_state.msgs = []
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("Асуултаа бичнэ үү..."):
        full_p = f"{context}\n\nАсуулт: {p}" if context else p
        st.session_state.msgs.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                           headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                           json={"model": "llama-3.3-70b-versatile", "messages": st.session_state.msgs})
        ans = res.json()['choices'][0]['message']['content']
        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.msgs.append({"role": "assistant", "content": ans})

# --- 3. 🌍 ПОРТАЛ (Шинэ сайтууд нэмэгдсэн) ---
elif menu == "🌍 Портал":
    st.title("🌍 Боловсролын Порталууд")
    t = st.tabs(["🗺️ EduMap", "🎥 Medle", "🎮 Eduten", "🇬🇧 EnglishConnect", "📝 Unelgee", "📚 Бусад"])
    with t[0]: components.iframe("https://edumap.mn/", height=800)
    with t[1]: components.iframe("https://medle.mn/", height=800)
    with t[2]: components.iframe("https://www.eduten.com/", height=800)
    with t[3]: components.iframe("https://englishconnect.pearson.com/", height=800)
    with t[4]: components.iframe("https://unelgee.eec.mn/auth/login/", height=800)
    with t[5]:
        st.markdown("- [E-Content](https://econtent.edu.mn/book)")
        st.markdown("- [Bagsh.edu.mn](https://bagsh.edu.mn/)")
        st.markdown("- [EEC.mn](https://www.eec.mn/)")

# Бусад модулиуд (Тест үүсгэгч) хэвээрээ...
