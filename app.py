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

# --- HTML/CSS УСНЫ АНИМАЦИ (HEADER) ---
water_effect_html = """
<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 30px; border-radius: 15px; position: relative; overflow: hidden; text-align: center; color: white; font-family: 'Poppins', sans-serif;">
    <style>
        .wave { position: absolute; bottom: 0; left: 0; width: 200%; height: 50px; 
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 120"><path d="M0,60 Q300,0 600,60 T1200,60 L1200,120 L0,120 Z" fill="%23ffffff" opacity="0.2"/></svg>') repeat-x;
            animation: wave 12s linear infinite; }
        @keyframes wave { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
    </style>
    <h1 style="margin:0; font-size: 2.2rem; text-shadow: 2px 2px 8px rgba(0,0,0,0.3);">🌊 EDUPLAN PRO AI</h1>
    <p style="opacity: 0.9; font-size: 1rem;">Боловсролын нэгдсэн портал ба AI төлөвлөгч</p>
    <div class="wave"></div>
</div>
"""

# --- СИСТЕМИЙН ҮНДСЭН CSS ---
st.markdown("""
    <style>
    .main { background-image: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 50%, #7dd3fc 100%); }
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    
    .approval-box { 
        text-align: right; font-family: 'Times New Roman', serif; 
        margin-bottom: 30px; line-height: 1.2; font-weight: bold; color: #1e293b;
    }

    .main-title { text-align: center; color: #1E3A8A; font-weight: 800; text-transform: uppercase; margin: 20px 0; }

    .stButton>button { 
        border-radius: 8px; background-image: linear-gradient(to right, #2563eb, #1d4ed8); 
        color: white; width: 100%; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); }

    /* Портал картын загвар */
    .portal-link {
        display: block; padding: 15px; background: white; border-radius: 10px;
        text-decoration: none; color: #1e3a8a; font-weight: bold;
        margin-bottom: 10px; border-left: 5px solid #2563eb;
        transition: 0.3s; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .portal-link:hover { transform: translateX(10px); background: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

# --- НЭВТРЭХ ФУНКЦ ---
def auth_ui():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated:
        components.html(water_effect_html, height=180)
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            with st.form("login_form"):
                st.markdown("<h3 style='text-align:center;'>Нэвтрэх</h3>", unsafe_allow_html=True)
                password = st.text_input("Нууц үг (admin1234):", type="password")
                if st.form_submit_button("Системд нэвтрэх"):
                    if password == "admin1234":
                        st.session_state.authenticated = True
                        st.rerun()
                    else: st.error("❌ Нууц үг буруу!")
        return False
    return True

if auth_ui():
    if 'history' not in st.session_state: st.session_state.history = []

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
                file = st.file_uploader("Сурах бичгийн PDF", type="pdf")
                grd = st.selectbox("Анги", [str(i) for i in range(1, 13)], index=5)
                tpc = st.text_input("Хичээлийн сэдэв")
                if st.button("🚀 Төлөвлөгөө гаргах"):
                    if file and tpc:
                        with st.spinner("AI боловсруулж байна..."):
                            reader = PyPDF2.PdfReader(file)
                            txt = "".join([p.extract_text() for p in reader.pages])
                            headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                            prompt = f"БАТЛАВ: СУРГАЛТЫН МЕНЕЖЕР Б. НАМУУН\nСэдэв: {tpc}, Анги: {grd}\nАгуулга: {txt[:5000]}"
                            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                            if res.status_code == 200:
                                st.session_state.current_view = res.json()['choices'][0]['message']['content']
                                st.session_state.history.append({"topic": tpc, "grd": grd, "date": str(datetime.date.today())})
                                st.rerun()

        with col_out:
            if 'current_view' in st.session_state:
                st.markdown("<div class='approval-box'>БАТЛАВ<br>СУРГАЛТЫН МЕНЕЖЕР ................... Б. НАМУУН</div>", unsafe_allow_html=True)
                st.markdown(st.session_state.current_view)
            else: st.info("👈 Мэдээллээ оруулна уу.")

    # --- 2. АНАЛИЗ ---
    elif menu == "📊 Миний Анализ":
        st.markdown("<h2 class='main-title'>Ажлын үзүүлэлт</h2>", unsafe_allow_html=True)
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.plotly_chart(px.bar(df['grd'].value_counts(), title="Ангиарх хуваарилалт"))
        else: st.info("Түүх байхгүй байна.")

    # --- 3. ПОРТАЛ (ШИНЭЧЛЭГДСЭН) ---
    elif menu == "🌍 Портал":
        st.markdown("<h2 class='main-title'>Боловсролын портал сайтууд</h2>", unsafe_allow_html=True)
        
        portals = {
            "📚 E-Content (Сурах бичиг)": "https://econtent.edu.mn/book",
            "💻 Medle.mn (Цахим сургалт)": "https://medle.mn/",
            "📊 EduMap (Боловсролын статистик)": "https://edumap.mn/",
            "👨‍🏫 Bagsh.edu.mn (Багшийн хөгжил)": "https://bagsh.edu.mn/"
        }

        col_list, col_view = st.columns([1, 2.5])

        with col_list:
            st.subheader("Сайт сонгох")
            for name, url in portals.items():
                if st.button(name):
                    st.session_state.active_portal = url
        
        with col_view:
            target_url = st.session_state.get('active_portal', "https://econtent.edu.mn/book")
            st.markdown(f"**Одоо үзэж буй:** {target_url}")
            components.iframe(target_url, height=800, scrolling=True)
