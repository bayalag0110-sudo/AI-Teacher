import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
from docx import Document
from io import BytesIO
import PyPDF2

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v5.2", layout="wide", page_icon="🎓")

# --- CUSTOM CSS (Өнгөний алдааг зассан шийдэл) ---
st.markdown("""
    <style>
    /* Үндсэн дэвсгэр */
    .stApp {
        background: linear-gradient(135deg, #1e3a8a 0%, #7e22ce 100%);
        background-attachment: fixed;
    }

    /* Sidebar - Цагаан дэвсгэр, Бараан текст */
    [data-testid="stSidebar"] {
        background-color: white !important;
    }
    [data-testid="stSidebar"] * {
        color: #1e293b !important;
    }

    /* Дотор талын цагаан картууд */
    .glass-card {
        background: white !important;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    
    /* Карт доторх бүх текст, шошгыг ХАР болгох */
    .glass-card label, .glass-card p, .glass-card h1, .glass-card h2, .glass-card h3, .glass-card span, .glass-card div {
        color: #1e293b !important;
    }

    /* Оролтын талбарууд (Input) */
    div.stTextInput input, div.stNumberInput input, div.stSelectbox div {
        color: black !important;
        background-color: #f8fafc !important;
    }

    /* Нэвтрэх хэсгийн Glassmorphism */
    .login-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        margin-top: 20px;
    }
    .login-card h1, .login-card p, .login-card label {
        color: white !important;
    }

    /* Товчлуур */
    .stButton>button {
        width: 100%;
        background-color: white !important;
        color: #1e3a8a !important;
        font-weight: 700;
        border-radius: 12px;
        border: none;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- WORD ФАЙЛ ҮҮСГЭХ ФУНКЦ ---
def create_word_doc(content, title):
    doc = Document()
    doc.add_heading(title, 0)
    doc.add_paragraph(content)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- НЭВТРЭХ ЛОГИК ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, login_col, _ = st.columns([1, 1.4, 1])
    with login_col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        try:
            # Логоны файлын нэрийг таны илгээсэн нэрээр тохируулав
            st.image('450633998_2213051369057631_4561852154062620515_n.jpg', width=160)
        except:
            st.markdown("<h1 style='font-size:4rem;'>🎓</h1>", unsafe_allow_html=True)
            
        st.markdown("<h1 style='margin-bottom:0;'>EduPlan Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='opacity:0.8;'>Дорноговь, Замын-Үүд 2-р сургууль</p>", unsafe_allow_html=True)
        
        u_role = st.radio("Та хэн бэ?", ["Багш", "Сурагч"], horizontal=True)
        u_name = st.text_input("👤 Хэрэглэгчийн нэр")
        u_pwd = st.text_input("🔑 Нууц үг", type="password")
        
        if st.button("СИСТЕМД НЭВТРЭХ"):
            if u_pwd == "admin1234" and u_name:
                st.session_state.auth = True
                st.session_state.role = u_role
                st.session_state.user = u_name
                st.rerun()
            else:
                st.error("Мэдээлэл буруу байна!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR МЕНЮ ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user}")
    st.write(f"📍 {st.session_state.role}")
    st.divider()
    menu = st.radio("ҮНДСЭН ЦЭС", ["💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "🤖 AI Чатбот", "🌍 Портал"])
    if st.button("🚪 Гарах"):
        st.session_state.auth = False
        st.rerun()

# --- МОДУЛИУД ---

# 1. ЭЭЛЖИТ ТӨЛӨВЛӨГЧ
if menu == "💎 Ээлжит төлөвлөгч":
    st.markdown("<h1 style='color:white;'>💎 Ээлжит хичээл төлөвлөлт</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        p_file = st.file_uploader("Сурах бичиг (PDF)", type="pdf")
        p_start = st.number_input("Эхлэх хуудас", 1, value=1)
        p_end = st.number_input("Дуусах хуудас", 1, value=3)
        p_tpc = st.text_input("Хичээлийн сэдэв")
        if st.button("🚀 Төлөвлөгөө гаргах"):
            if p_file and p_tpc:
                with st.spinner("AI ажиллаж байна..."):
                    reader = PyPDF2.PdfReader(p_file)
                    txt = "".join([reader.pages[i].extract_text() for i in range(p_start-1, min(p_end, len(reader.pages)))])
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"Текст: {txt[:5000]}. Сэдэв: {p_tpc}. Хичээлийн төлөвлөгөө гарга."}]})
                    st.session_state.last_plan = res.json()['choices'][0]['message']['content']
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'last_plan' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.last_plan)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.last_plan, p_tpc), f"{p_tpc}.docx")
            st.markdown('</div>', unsafe_allow_html=True)

# 2. ТЕСТ ҮҮСГЭГЧ
elif menu == "📝 Тест үүсгэгч":
    st.markdown("<h1 style='color:white;'>📝 Тест боловсруулах</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t_file = st.file_uploader("PDF файл", type="pdf", key="test_up")
        t_num = st.slider("Асуултын тоо", 5, 20, 10)
        if st.button("🎯 Тест үүсгэх"):
            if t_file:
                with st.spinner("Асуултууд бэлдэж байна..."):
                    reader = PyPDF2.PdfReader(t_file)
                    txt = "".join([p.extract_text() for p in reader.pages[:3]])
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                       headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                       json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"Текст: {txt[:5000]}. {t_num} тест зохиож, хариуг бич."}]})
                    st.session_state.last_test = res.json()['choices'][0]['message']['content']
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'last_test' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.last_test)
            st.download_button("📥 Word татах", create_word_doc(st.session_state.last_test, "Тест"), "test.docx")
            st.markdown('</div>', unsafe_allow_html=True)

# 3. AI ЧАТБОТ
elif menu == "🤖 AI Чатбот":
    st.markdown("<h1 style='color:white;'>🤖 AI Туслах</h1>", unsafe_allow_html=True)
    if "msgs" not in st.session_state: st.session_state.msgs = []
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if p := st.chat_input("Асуух зүйлээ бичнэ үү..."):
        st.session_state.msgs.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                           headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                           json={"model": "llama-3.3-70b-versatile", "messages": st.session_state.msgs})
        ans = res.json()['choices'][0]['message']['content']
        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.msgs.append({"role": "assistant", "content": ans})

# 4. ПОРТАЛ
elif menu == "🌍 Портал":
    st.markdown("<h1 style='color:white;'>🌍 Боловсролын Порталууд</h1>", unsafe_allow_html=True)
    tabs = st.tabs(["📚 E-Content", "👨‍🏫 Bagsh.edu.mn", "✅ Unelgee", "📊 EEC", "📑 ESIS"])
    with tabs[0]: components.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)
    with tabs[1]: components.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)
    with tabs[2]: components.iframe("https://unelgee.eec.mn/", height=800, scrolling=True)
    with tabs[3]: components.iframe("https://www.eec.mn/", height=800, scrolling=True)
    with tabs[4]: st.info("ESIS систем хаягаар хандана уу: esis.edu.mn")
