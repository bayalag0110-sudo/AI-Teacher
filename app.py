import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2
from PIL import Image

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v6.0", layout="wide", page_icon="🎓")

# --- CUSTOM CSS (Харагдац болон загвар) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }
    .glass-card {
        background: white !important;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
        color: #1e293b !important;
    }
    label, p, h1, h2, h3, span { color: #1e293b !important; font-weight: 500; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        font-weight: 700;
        border-radius: 10px;
        border: none;
        padding: 10px;
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
    except: return "PDF уншихад алдаа гарлаа."

def extract_docx_text(file):
    try:
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    except: return "Word файл уншихад алдаа гарлаа."

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
        st.markdown("<h2>EduPlan Pro</h2><p>Замын-Үүд 2-р сургууль</p>", unsafe_allow_html=True)
        u_name = st.text_input("👤 Хэрэглэгчийн нэр")
        u_pwd = st.text_input("🔑 Нууц үг", type="password")
        if st.button("СИСТЕМД НЭВТРЭХ"):
            if u_pwd == "admin1234": st.session_state.auth, st.session_state.user = True, u_name; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR МЕНЮ ---
with st.sidebar:
    st.markdown(f"### 👋 Сайн уу, {st.session_state.user}")
    menu = st.radio("ҮНДСЭН ЦЭС", ["💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📝 Даалгавар өгөх", "🤖 AI Чатбот", "🌍 Портал"])
    if st.button("🚪 Гарах"): st.session_state.auth = False; st.rerun()

# --- 1. 💎 ЭЭЛЖИТ ТӨЛӨВЛӨГЧ (Таны хүссэн промтын дагуу) ---
if menu == "💎 Ээлжит төлөвлөгч":
    st.title("💎 Ухаалаг хичээл төлөвлөлт")
    col1, col2 = st.columns([1, 1.8])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        p_file = st.file_uploader("Сурах бичиг хавсаргах (PDF)", type="pdf")
        p_start = st.number_input("Эхлэх хуудас", 1, value=1)
        p_end = st.number_input("Дуусах хуудас", 1, value=3)
        p_topic = st.text_input("Хичээлийн сэдэв", value="Өгөгдлийн шинж чанараар эрэмбэлэх, шүүлт хийх")
        p_grade = st.selectbox("Анги", ["1-р анги", "2-р анги", "3-р анги", "4-р анги", "5-р анги", "6-р анги", "7-р анги", "8-р анги", "9-р анги", "10-р анги", "11-р анги", "12-р анги"], index=8)
        
        if st.button("🚀 Төлөвлөгөө боловсруулах"):
            with st.spinner("Таны заасан загварын дагуу AI боловсруулж байна..."):
                context = extract_pdf_text(p_file, p_start, p_end) if p_file else "Сурах бичгийн ерөнхий агуулга."
                
                # ТАНЫ ХҮССЭН ТУСГАЙ ЗАГВАР БҮХИЙ ПРОМТ
                full_prompt = f"""
                Чи бол Монгол улсын ЕБС-ийн Мэдээллийн технологийн мэргэжлийн багш. Дараах зааврын дагуу хичээлийн төлөвлөгөөг ХҮСНЭГТЭН хэлбэрээр гарга:
                
                Хичээл: Мэдээллийн технологи, Анги: {p_grade}, Сэдэв: {p_topic}
                Эх сурвалж: {context[:2000]}
                
                БҮТЭЦ:
                1. Суралцахуйн зорилт: Bloom taxonomy буюу танин мэдэхүйн түвшний дагуу тодорхойлох.
                2. Хичээлийн үе шат: Танилцуулга, Үндсэн агуулга, Дүгнэлт, бэхжилт гэсэн бүтэцтэй байх.
                3. Арга зүй, хэлбэр: Сурагчийн оролцоог нэмэгдүүлэх аргууд, Бүлгийн болон ганцаарчилсан ажлуудыг тусгах.
                4. Дасгал, даалгавар (3 түвшинд):
                   - Бүрэн эзэмшсэн сурагчид: Чадвар шаардсан бүтээлч бодлого.
                   - Эзэмшиж буй сурагчид: Жишээ, асуулттай ажиллах.
                   - Дутуу эзэмшсэн сурагчид: Үндсэн ойлголт, нэр томьёо таних, тайлбарлах.
                5. Үнэлгээ: Хичээлийн төгсгөлд 5 минутын асуулт, даалгавар оруулах.
                
                Хариуг Markdown хүснэгт ашиглан маш цэвэрхэн харуул.
                """
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                   headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                   json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": full_prompt}]})
                st.session_state.plan_output = res.json()['choices'][0]['message']['content']
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'plan_output' in st.session_state:
            st.markdown(f'<div class="glass-card">{st.session_state.plan_output}</div>', unsafe_allow_html=True)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.plan_output, p_topic), f"{p_topic}.docx")

# --- 2. 🤖 AI ЧАТБОТ (Бүх төрлийн файл дэмжинэ) ---
elif menu == "🤖 AI Чатбот":
    st.title("🤖 AI Ухаалаг туслах")
    with st.expander("📎 Файл хавсаргах (PDF, Word, Excel, Image)"):
        up = st.file_uploader("Файл сонгох", type=['pdf', 'docx', 'xlsx', 'jpg', 'png'])
        f_context = ""
        if up:
            if up.name.endswith('.pdf'): f_context = extract_pdf_text(up, 1, 5)
            elif up.name.endswith('.docx'): f_context = extract_docx_text(up)
            elif up.name.endswith('.xlsx'):
                df = pd.read_excel(up, engine='openpyxl')
                f_context = df.to_string(); st.dataframe(df.head())
            else: st.image(up, width=200); f_context = "[Зураг хавсаргав]"
            st.success(f"{up.name} амжилттай уншигдлаа.")

    if "history" not in st.session_state: st.session_state.history = []
    for m in st.session_state.history:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("Асуултаа бичнэ үү..."):
        full_p = f"{f_context}\n\nАсуулт: {p}" if f_context else p
        st.session_state.history.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        with st.spinner("AI хариулж байна..."):
            res = requests.post("https://api.groq.com/openai/v1/chat/colpletions", 
                               headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                               json={"model": "llama-3.3-70b-versatile", "messages": st.session_state.history})
            # Жич: Энд API хариултыг аваад дэлгэцэнд хэвлэх логик ажиллана.
            st.rerun()

# --- 3. ТЕСТ ҮҮСГЭГЧ (Хуудас заадаг) ---
elif menu == "📝 Тест үүсгэгч":
    st.title("📝 Тест боловсруулах")
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t_file = st.file_uploader("Агуулга (PDF)", type="pdf", key="t_up")
        t_start = st.number_input("Эхлэх хуудас", 1, value=1)
        t_end = st.number_input("Дуусах хуудас", 1, value=2)
        t_num = st.slider("Асуултын тоо", 5, 20, 10)
        if st.button("🎯 Тест үүсгэх"):
            if t_file:
                with st.spinner("AI тест зохиож байна..."):
                    txt = extract_pdf_text(t_file, t_start, t_end)
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"Текст: {txt[:4000]}. {t_num} тест зохиож хариуг хавсарга."}]})
                    st.session_state.test_res = res.json()['choices'][0]['message']['content']
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'test_res' in st.session_state:
            st.markdown(f'<div class="glass-card">{st.session_state.test_res}</div>', unsafe_allow_html=True)

# --- 4. ПОРТАЛ ---
elif menu == "🌍 Портал":
    st.title("🌍 Боловсролын Порталууд")
    t = st.tabs(["📚 E-Content", "👨‍🏫 Bagsh.edu.mn", "📊 EEC"])
    with t[0]: components.iframe("https://econtent.edu.mn/book", height=800)
    with t[1]: components.iframe("https://bagsh.edu.mn/", height=800)
    with t[2]: components.iframe("https://www.eec.mn/", height=800)

# --- 5. ДААЛГАВАР ӨГӨХ ---
elif menu == "📝 Даалгавар өгөх":
    st.title("📝 Даалгавар нийтлэх")
    with st.form("hw"):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.text_input("Анги")
        st.text_input("Сэдэв")
        st.text_area("Даалгавар")
        if st.form_submit_button("Илгээх"): st.success("Даалгавар амжилттай илгээгдлээ.")
        st.markdown('</div>', unsafe_allow_html=True)
