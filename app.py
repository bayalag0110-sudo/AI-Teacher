import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2

# 1. Хуудасны үндсэн тохиргоо
st.set_page_config(page_title="EduPlan Pro AI v2.5", layout="wide", page_icon="🎓")

# --- CUSTOM CSS (Glassmorphism & Theme) ---
if 'theme' not in st.session_state: 
    st.session_state.theme = 'light'

theme_css = {
    'light': {
        'bg': 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #bae6fd 100%)',
        'card': 'rgba(255, 255, 255, 0.75)',
        'text': '#0f172a',
        'sidebar': '#ffffff'
    },
    'dark': {
        'bg': 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
        'card': 'rgba(30, 41, 59, 0.7)',
        'text': '#f8fafc',
        'sidebar': '#1e293b'
    }
}
curr = theme_css[st.session_state.theme]

st.markdown(f"""
    <style>
    .stApp {{ background-image: {curr['bg']}; color: {curr['text']}; }}
    section[data-testid="stSidebar"] {{ background-color: {curr['sidebar']} !important; }}
    
    .glass-card {{
        background: {curr['card']};
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        margin-bottom: 20px;
    }}
    
    .main-title {{
        text-align: center;
        background: linear-gradient(to right, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 1rem;
    }}
    
    .stButton>button {{
        border-radius: 12px;
        background: linear-gradient(45deg, #2563eb, #7c3aed);
        color: white;
        border: none;
        padding: 12px 24px;
        width: 100%;
        font-weight: bold;
        transition: 0.3s ease;
    }}
    .stButton>button:hover {{ transform: scale(1.02); box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4); }}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER WITH WATER EFFECT ---
water_header = f"""
<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 30px; border-radius: 20px; position: relative; overflow: hidden; text-align: center; color: white; font-family: 'Poppins', sans-serif;">
    <h1 style="margin:0; font-size: 2.2rem; text-shadow: 2px 2px 8px rgba(0,0,0,0.3);">🌊 EDUPLAN PRO AI</h1>
    <p style="opacity: 0.9;">Ухаалаг багшийн цогц систем</p>
</div>
"""

# --- LOGIN LOGIC ---
if "authenticated" not in st.session_state: 
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    components.html(water_header, height=180)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center;'>Системд нэвтрэх</h3>", unsafe_allow_html=True)
        pwd = st.text_input("Нууц үг:", type="password")
        if st.button("Нэвтрэх"):
            if pwd == "admin1234":
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("❌ Нууц үг буруу байна!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ✨ Сайн байна уу")
    if st.button("🌓 Горим солих"):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()
    st.divider()
    menu = st.radio("ҮНДСЭН ЦЭС", ["💎 Төлөвлөгч", "📝 Тест үүсгэгч", "📊 Миний сан", "🌍 Портал"])
    st.divider()
    if st.button("🚪 Системээс гарах"):
        st.session_state.authenticated = False
        st.rerun()

# --- 1. ТӨЛӨВЛӨГЧ ---
if menu == "💎 Төлөвлөгч":
    st.markdown("<h1 class='main-title'>Ээлжит хичээл боловсруулах</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.6])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        file = st.file_uploader("Сурах бичиг (PDF)", type="pdf", key="plan_up")
        l_type = st.selectbox("Хичээлийн хэв шинж", ["Шинэ мэдлэг олгох", "Батгах хичээл", "Лаборатори/Практик", "Шалгалт/Сорил"])
        tpc = st.text_input("Хичээлийн сэдэв")
        if st.button("🚀 Төлөвлөгөө гаргах"):
            if file and tpc:
                with st.spinner("AI төлөвлөгөө боловсруулж байна..."):
                    reader = PyPDF2.PdfReader(file)
                    txt = "".join([p.extract_text() for p in reader.pages[:15]])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"БАТЛАВ: МЕНЕЖЕР Б. НАМУУН\nТөрөл: {l_type}\nСэдэв: {tpc}\nАгуулга: {txt[:6000]}\nСтандарт төлөвлөгөө гарга."
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    if res.status_code == 200:
                        st.session_state.current_plan = res.json()['choices'][0]['message']['content']
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if 'current_plan' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<div style='text-align:right; font-weight:bold;'>БАТЛАВ: МЕНЕЖЕР Б. НАМУУН</div>", unsafe_allow_html=True)
            st.markdown(st.session_state.current_plan)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 2. ТЕСТ ҮҮСГЭГЧ (ХУУДАСНЫ ИНТЕРВАЛТАЙ) ---
elif menu == "📝 Тест үүсгэгч":
    st.markdown("<h1 class='main-title'>Нарийвчилсан тест үүсгэгч</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.6])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t_file = st.file_uploader("Сурах бичиг (PDF)", type="pdf", key="test_up")
        
        st.write("📖 Унших хуудасны интервал:")
        c_p1, c_p2 = st.columns(2)
        with c_p1: start_pg = st.number_input("Эхлэх", min_value=1, value=1)
        with c_p2: end_pg = st.number_input("Дуусах", min_value=1, value=5)
            
        t_tpc = st.text_input("Тестийн сэдэв")
        t_format = st.multiselect("Тестийн хэлбэр", 
                                ["Нэг сонголттой (A,B,C,D)", "Олон хариулттай", "Нөхөх даалгавар", "Зөв/Буруу"],
                                default=["Нэг сонголттой (A,B,C,D)"])
        t_count = st.slider("Асуултын тоо", 5, 20, 10)
        
        if st.button("🎯 Тест боловсруулах"):
            if t_file and t_tpc:
                with st.spinner(f"PDF-ийн {start_pg}-{end_pg} хуудсыг шинжилж байна..."):
                    reader = PyPDF2.PdfReader(t_file)
                    extracted_text = ""
                    total_pages = len(reader.pages)
                    s_idx = max(0, start_pg - 1)
                    e_idx = min(total_pages, end_pg)
                    
                    for i in range(s_idx, e_idx):
                        extracted_text += reader.pages[i].extract_text()
                    
                    if len(extracted_text.strip()) > 50:
                        headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                        prompt = f"""
                        Чи бол Боловсролын Үнэлгээний Мэргэжилтэн.
                        Даалгавар: Оруулсан эх текстэд тулгуурлан {t_tpc} сэдвээр {t_count} асуулттай тест бэлд.
                        
                        Хэлбэрүүд: {', '.join(t_format)}.
                        
                        ХАТУУ АНХААРУУЛГА: 
                        1. Эх текст доторх гарчиг, дэд гарчиг, бүлгийн нэрийг асуулт эсвэл хариулт болгож шууд хуулж болохгүй!
                        2. Агуулга доторх баримт, ойлголтыг ашиглан шинээр асуулт боловсруул.
                        3. Сонгох хариултууд логиктой, хоорондоо ялгаатай байх ёстой.
                        
                        ЭХ ТЕКСТ:
                        {extracted_text[:10000]}
                        """
                        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                          headers=headers, 
                                          json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1})
                        if res.status_code == 200:
                            st.session_state.generated_test = res.json()['choices'][0]['message']['content']
                            st.rerun()
                    else: st.error("Хуудаснаас текст уншиж чадсангүй!")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if 'generated_test' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.generated_test)
            doc = Document(); doc.add_paragraph(st.session_state.generated_test)
            bio = BytesIO(); doc.save(bio)
            st.download_button("📥 Word татах", bio.getvalue(), "test.docx")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 3. ПОРТАЛ ---
elif menu == "🌍 Портал":
    st.markdown("<h2 class='main-title'>Боловсролын порталууд</h2>", unsafe_allow_html=True)
    tabs = st.tabs(["📚 E-Content", "💻 Medle.mn", "👨‍🏫 Bagsh.edu.mn", "📊 Edumap.mn"])
    with tabs[0]: components.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)
    with tabs[1]: components.iframe("https://medle.mn/", height=800, scrolling=True)
    with tabs[2]: components.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)
    with tabs[3]: components.iframe("https://edumap.mn/", height=800, scrolling=True)

# --- 4. МИНИЙ САН ---
elif menu == "📊 Миний сан":
    st.markdown("<h1 class='main-title'>Миний хадгалсан файлууд</h1>", unsafe_allow_html=True)
    st.info("Тун удахгүй: Таны боловсруулсан бүх төлөвлөгөө, тестүүд энд датабаазад хадгалагдах болно.")
