import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2
import plotly.express as px

# 1. Хуудасны үндсэн тохиргоо
st.set_page_config(page_title="EduPlan Pro AI", layout="wide", page_icon="🎓")

# --- HTML/CSS УСНЫ АНИМАЦИ ---
water_effect_html = """
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; border-radius: 15px; position: relative; overflow: hidden; text-align: center; color: white; font-family: 'Poppins', sans-serif;">
    <style>
        .wave { position: absolute; bottom: 0; left: 0; width: 200%; height: 60px; 
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 120"><path d="M0,60 Q300,0 600,60 T1200,60 L1200,120 L0,120 Z" fill="%23ffffff" opacity="0.3"/></svg>') repeat-x;
            animation: wave 10s linear infinite; }
        @keyframes wave { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        .bubble { position: absolute; bottom: -20px; background: rgba(255,255,255,0.2); border-radius: 50%; animation: float 5s infinite; }
        @keyframes float { 0% { transform: translateY(0); opacity: 1; } 100% { transform: translateY(-100px); opacity: 0; } }
    </style>
    <div class="bubble" style="width:20px; height:20px; left:10%;"></div>
    <div class="bubble" style="width:30px; height:30px; left:50%; animation-delay:2s;"></div>
    <h1 style="margin:0; font-size: 2.5rem; text-shadow: 2px 2px 10px rgba(0,0,0,0.3);">🌊 EDUPLAN PRO AI</h1>
    <p style="opacity: 0.9;">Орчин үеийн ухаалаг төлөвлөлтийн систем</p>
    <div class="wave"></div>
</div>
"""

# --- СИСТЕМИЙН ҮНДСЭН CSS ---
st.markdown("""
    <style>
    /* Вебийн үндсэн дэвсгэр */
    .main { 
        background-image: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 50%, #7dd3fc 100%); 
    }
    
    /* Sidebar загвар */
    section[data-testid="stSidebar"] { 
        background-color: #ffffff !important; 
        border-right: 1px solid #e0e0e0; 
    }
    
    /* Батлав хэсэг (Яг загвар дээрх шиг) */
    .approval-box { 
        text-align: right; 
        font-family: 'Times New Roman', serif; 
        margin-bottom: 30px; 
        line-height: 1.2; 
        font-weight: bold; 
        color: #1e293b;
    }

    /* Гарчиг */
    .main-title { 
        text-align: center; 
        color: #1E3A8A; 
        font-weight: 800; 
        text-transform: uppercase; 
        margin: 20px 0; 
    }

    /* Товчлуур */
    .stButton>button { 
        border-radius: 8px; 
        background-image: linear-gradient(to right, #2563eb, #1d4ed8); 
        color: white; 
        width: 100%; 
        font-weight: bold;
    }
    
    /* Карт хэлбэртэй контейнер */
    [data-testid="stVerticalBlock"] > div:has(div.stForm) {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- НЭВТРЭХ ФУНКЦ ---
def auth_ui():
    if "authenticated" not in st.session_state: 
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        # Усны анимаци нэвтрэх хэсгийн дээр харагдана
        components.html(water_effect_html, height=220)
        
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            with st.form("login_form"):
                st.markdown("<h3 style='text-align:center;'>Системд нэвтрэх</h3>", unsafe_allow_html=True)
                password = st.text_input("Нууц үг:", type="password")
                submit = st.form_submit_button("Нэвтрэх")
                if submit:
                    if password == "admin1234":
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("❌ Нууц үг буруу байна!")
        return False
    return True

if auth_ui():
    if 'history' not in st.session_state: 
        st.session_state.history = []

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("### ✨ Сайн байна уу, Багшаа")
        if st.button("🚪 Системээс гарах"):
            st.session_state.authenticated = False
            st.rerun()
        st.divider()
        menu = st.radio("ҮНДСЭН ЦЭС", ["💎 Төлөвлөгч", "📊 Миний Анализ", "🌍 Портал"])

    # --- 1. ТӨЛӨВЛӨГЧ ---
    if menu == "💎 Төлөвлөгч":
        st.markdown("<h2 class='main-title'>Ээлжит хичээл боловсруулах</h2>", unsafe_allow_html=True)
        col_in, col_out = st.columns([1, 1.4])
        
        with col_in:
            with st.container(border=True):
                st.subheader("📂 Материал оруулах")
                file = st.file_uploader("Сурах бичгийн PDF", type="pdf")
                grd = st.selectbox("Анги", [str(i) for i in range(1, 13)], index=5)
                tpc = st.text_input("Хичээлийн сэдэв")
                
                if st.button("🚀 Төлөвлөгөө гаргах"):
                    if file and tpc:
                        with st.spinner("AI агуулгыг боловсруулж байна..."):
                            reader = PyPDF2.PdfReader(file)
                            txt = "".join([p.extract_text() for p in reader.pages])
                            headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                            prompt = f"""
                            БАТЛАВ: СУРГАЛТЫН МЕНЕЖЕР Б. НАМУУН
                            Сэдэв: {tpc}, Анги: {grd}
                            70/30 арга зүйгээр, Эхлэл(5'), Өрнөл(25'), Төгсгөл(10') бүтцээр төлөвлөгөө гарга.
                            Агуулга: {txt[:6000]}
                            """
                            res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                              headers=headers, 
                                              json={"model": "llama-3.3-70b-versatile", 
                                                    "messages": [{"role": "user", "content": prompt}]})
                            if res.status_code == 200:
                                result = res.json()['choices'][0]['message']['content']
                                st.session_state.current_view = result
                                st.session_state.history.append({"topic": tpc, "grd": grd, "date": str(datetime.date.today())})
                                st.rerun()

        with col_out:
            if 'current_view' in st.session_state:
                st.markdown("<div class='approval-box'>БАТЛАВ<br>СУРГАЛТЫН МЕНЕЖЕР ................... Б. НАМУУН</div>", unsafe_allow_html=True)
                st.markdown(st.session_state.current_view)
                
                doc = Document(); doc.add_paragraph(st.session_state.current_view)
                bio = BytesIO(); doc.save(bio)
                st.download_button("📥 Word татах", bio.getvalue(), "lesson_plan.docx")
            else:
                st.info("👈 Зүүн талд мэдээллээ оруулна уу.")

    # --- 2. АНАЛИЗ ---
    elif menu == "📊 Миний Анализ":
        st.markdown("<h2 class='main-title'>Ажлын үзүүлэлт</h2>", unsafe_allow_html=True)
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.plotly_chart(px.bar(df['grd'].value_counts(), title="Ангиарх хуваарилалт"))
        else:
            st.info("Түүх байхгүй байна.")

    # --- 3. ПОРТАЛ ---
    elif menu == "🌍 Портал":
        st.components.v1.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)
