import streamlit as st
import requests
import datetime
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2
import plotly.express as px

# 1. Хуудасны үндсэн тохиргоо
st.set_page_config(page_title="EduPlan Pro AI", layout="wide", page_icon="💡")

# --- CUSTOM CSS (Загваржуулалт) ---
st.markdown("""
    <style>
    /* Үндсэн фонт болон арын дэвсгэр */
    .main { background-color: #f8f9fa; }
    
    /* Sidebar загвар */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Карт болон контейнер */
    .st-emotion-cache-12w0qpk { 
        padding: 1.5rem; 
        border-radius: 15px; 
        background: white; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Батлах хэсгийн загвар (Загвар.docx-оос) */
    .approval-box {
        text-align: right;
        font-family: 'Times New Roman', serif;
        margin-bottom: 30px;
        line-height: 1.2;
    }

    /* Гарчиг */
    .main-title {
        text-align: center;
        color: #1E3A8A;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 20px 0;
    }

    /* Портал холбоосууд */
    .portal-card {
        padding: 12px;
        border-radius: 10px;
        background: #f1f5f9;
        border-left: 5px solid #3b82f6;
        margin-bottom: 10px;
        transition: all 0.3s ease;
        text-decoration: none;
        display: block;
        color: #1e293b;
    }
    .portal-card:hover {
        background: #e2e8f0;
        transform: translateX(5px);
    }
    
    /* Товчлуур */
    .stButton>button {
        border-radius: 8px;
        background-image: linear-gradient(to right, #2563eb, #1d4ed8);
        color: white;
        font-weight: 600;
        border: none;
        transition: 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

# --- USER DB & AUTH ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {"admin": "admin123"}

def auth_ui():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("<h1 class='main-title'>EDUPLAN PRO AI</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            tab1, tab2 = st.tabs(["🔑 Нэвтрэх", "📝 Бүртгүүлэх"])
            with tab1:
                u = st.text_input("Хэрэглэгчийн нэр", key="l_u")
                p = st.text_input("Нууц үг", type="password", key="l_p")
                if st.button("Нэвтрэх", use_container_width=True):
                    if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                        st.session_state.authenticated = True
                        st.session_state.username = u
                        st.rerun()
                    else: st.error("Буруу байна")
            with tab2:
                nu = st.text_input("Шинэ нэр", key="s_u")
                np = st.text_input("Шинэ нууц үг", type="password", key="s_p")
                if st.button("Бүртгүүлэх", use_container_width=True):
                    if nu and np:
                        st.session_state.user_db[nu] = np
                        st.success("Бүртгэгдлээ!")
        return False
    return True

if auth_ui():
    if 'history' not in st.session_state: st.session_state.history = []

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"### ✨ Сайн байна уу, {st.session_state.username}")
       
            st.session_state.authenticated = False
            st.rerun()
        
        st.divider()
        menu = st.radio("ҮНДСЭН ЦЭС", ["💎 Төлөвлөгч", "📊 Миний Анализ", "🌍 Портал"], label_visibility="collapsed")
        
        st.divider()
        st.subheader("🌐 Хурдан холбоос")
        portals = {
            "📚 Econtent": "https://econtent.edu.mn/book",
            "💻 Medle.mn": "https://medle.mn/",
            "📊 EduMap": "https://edumap.mn/"
        }
        for n, u in portals.items():
            st.markdown(f'<a href="{u}" target="_blank" class="portal-card">{n}</a>', unsafe_allow_html=True)

    # --- 1. ТӨЛӨВЛӨГЧ ХЭСЭГ ---
    if menu == "💎 Төлөвлөгч":
        st.markdown("<h2 class='main-title'>Ээлжит хичээл боловсруулах</h2>", unsafe_allow_html=True)
        
        col_in, col_out = st.columns([1, 1.3])
        
        with col_in:
            with st.container(border=True):
                st.subheader("📂 Материал оруулах")
                file = st.file_uploader("Сурах бичгийн PDF", type="pdf")
                sub = st.text_input("Хичээлийн нэр", "Мэдээлэл зүй")
                grd = st.selectbox("Анги", [str(i) for i in range(1, 13)], index=5)
                tpc = st.text_input("Хичээлийн сэдэв")
                
                if st.button("✨ Боловсруулах", use_container_width=True):
                    if file and tpc:
                        with st.spinner("AI агуулгыг шинжилж байна..."):
                            reader = PyPDF2.PdfReader(file)
                            txt = "".join([p.extract_text() for p in reader.pages])
                            
                            # API Дуудлага (Groq)
                            headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                            prompt = f"""[БАТЛАВ: СУРГАЛТЫН МЕНЕЖЕР Б. НАМУУН]
                            Зөвхөн PDF-д тулгуурлан, 70/30 харьцаатай төлөвлөгөө гарга.
                            Бүтэц: Анги, Сэдэв, Зорилго, Үйл явц (Хүснэгтээр: Эхлэл 5', Өрнөл 25', Төгсгөл 10'), 
                            Гэрийн даалгавар, Ялгаатай сурагчдын аргачлал, Багшийн дүгнэлт.
                            PDF Текст: {txt[:7000]}"""
                            
                            res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                              headers=headers, 
                                              json={"model": "llama-3.3-70b-versatile", 
                                                    "messages": [{"role": "user", "content": prompt}],
                                                    "temperature": 0.1})
                            
                            if res.status_code == 200:
                                result = res.json()['choices'][0]['message']['content']
                                entry = {"topic": tpc, "grd": grd, "content": result, "date": str(datetime.date.today())}
                                st.session_state.history.append(entry)
                                st.session_state.current_view = entry
                                st.rerun()

        with col_out:
            if 'current_view' in st.session_state:
                item = st.session_state.current_view
                # БАТЛАВ хэсгийг харуулах (Загвар.docx-оос)
                st.markdown("""
                    <div class='approval-box'>
                        БАТЛАВ<br>
                        СУРГАЛТЫН МЕНЕЖЕР ................... Б. НАМУУН
                    </div>
                """, unsafe_allow_html=True) [cite: 1, 2]
                
                st.markdown(f"### {item['topic']}")
                st.markdown(item['content'])
                
                # Word Татах
                doc = Document()
                doc.add_paragraph(item['content'])
                bio = BytesIO()
                doc.save(bio)
                st.download_button("📥 Word хэлбэрээр татах", bio.getvalue(), f"{item['topic']}.docx")

    # --- 2. АНАЛИЗ ХЭСЭГ ---
    elif menu == "📊 Миний Анализ":
        st.markdown("<h2 class='main-title'>Таны ажлын үзүүлэлт</h2>", unsafe_allow_html=True)
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Нийт боловсруулсан", len(df))
                fig = px.bar(df['grd'].value_counts(), title="Ангиарх хуваарилалт")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.metric("Сүүлийн огноо", df.iloc[-1]['date'])
                fig2 = px.pie(df, names='grd', hole=0.4, title="Хичээлийн бүтэц")
                st.plotly_chart(fig2, use_container_width=True)
        else: st.info("Мэдээлэл байхгүй байна.")

    # --- 3. ПОРТАЛ ХЭСЭГ ---
    elif menu == "🌍 Портал":
        choice = st.selectbox("Платформ сонгох", list(portals.keys()))
        st.components.v1.iframe(portals[choice], height=800, scrolling=True)

