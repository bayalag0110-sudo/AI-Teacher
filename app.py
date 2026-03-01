import streamlit as st
import requests
import datetime
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2
import plotly.express as px

# 1. Хуудасны үндсэн тохиргоо
st.set_page_config(page_title="EduPlan Pro AI", layout="wide", page_icon="🎓")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    .approval-box { text-align: right; font-family: 'Times New Roman', serif; margin-bottom: 20px; line-height: 1.2; font-weight: bold; }
    .main-title { text-align: center; color: #1E3A8A; font-weight: 800; text-transform: uppercase; margin: 20px 0; }
    .portal-card { padding: 10px; border-radius: 8px; background: #f1f5f9; border-left: 5px solid #3b82f6; margin-bottom: 8px; text-decoration: none; display: block; color: #1e293b; font-weight: bold; }
    .stButton>button { border-radius: 8px; background-image: linear-gradient(to right, #2563eb, #1d4ed8); color: white; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- НЭВТРЭХ ХЭСЭГ (PASSWORD: admin1234) ---
def auth_ui():
    if "authenticated" not in st.session_state: 
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("<h1 class='main-title'>EDUPLAN PRO AI</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.info("🔐 Системд нэвтрэх")
            password = st.text_input("Нууц үгээ оруулна уу:", type="password")
            if st.button("Нэвтрэх"):
                # Таны хүссэн нууц үг: admin1234
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
        if st.button("🚪 Гарах"):
            st.session_state.authenticated = False
            st.rerun()
        
        st.divider()
        menu = st.radio("ҮНДСЭН ЦЭС", ["💎 Төлөвлөгч", "📊 Миний Анализ", "🌍 Портал"])
        
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
                
                if st.button("🚀 Боловсруулах"):
                    if file and tpc:
                        with st.spinner("AI агуулгыг шинжилж байна..."):
                            reader = PyPDF2.PdfReader(file)
                            txt = "".join([p.extract_text() for p in reader.pages])
                            
                            headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                            prompt = f"""
                            Чи бол Монгол улсын Боловсролын шинжээч багш. 
                            Дараах бүтцээр ээлжит хичээлийн төлөвлөгөөг PDF агуулгад тулгуурлан гарга:
                            1. БАТЛАВ: СУРГАЛТЫН МЕНЕЖЕР Б. НАМУУН
                            2. ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ (Анги, Сэдэв, Зорилго)
                            3. Үйл явц (Хүснэгтээр):
                               - Эхлэл (5 мин): Сэдэлжүүлэг
                               - Өрнөл (25 мин): Мэдлэг бүтээх (Сурагчийн оролцоо 70%)
                               - Төгсгөл (10 мин): Дүгнэлт
                            4. Гэрийн даалгавар, Ялгаатай сурагчидтай ажиллах арга, Багшийн дүгнэлт.
                            PDF Текст: {txt[:7000]}
                            Сэдэв: {tpc}
                            """
                            
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
                st.markdown("<div class='approval-box'>БАТЛАВ<br>СУРГАЛТЫН МЕНЕЖЕР ................... Б. НАМУУН</div>", unsafe_allow_html=True)
                st.markdown(f"### {item['topic']}")
                st.markdown(item['content'])
                
                doc = Document()
                doc.add_paragraph(item['content'])
                bio = BytesIO()
                doc.save(bio)
                st.download_button("📥 Word татах", bio.getvalue(), f"{item['topic']}.docx")
            else:
                st.info("👈 PDF файлаа оруулж, боловсруулах товчийг дарна уу.")

    # --- 2. АНАЛИЗ ХЭСЭГ ---
    elif menu == "📊 Миний Анализ":
        st.markdown("<h2 class='main-title'>Ажлын үзүүлэлт</h2>", unsafe_allow_html=True)
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Нийт боловсруулсан", len(df))
                st.plotly_chart(px.bar(df['grd'].value_counts(), title="Ангиарх хуваарилалт"), use_container_width=True)
            with c2:
                st.metric("Сүүлийн огноо", df.iloc[-1]['date'])
                st.plotly_chart(px.pie(df, names='grd', hole=0.4, title="Хичээлийн бүтэц"), use_container_width=True)
        else:
            st.info("Одоогоор түүх байхгүй байна.")

    # --- 3. ПОРТАЛ ХЭСЭГ ---
    elif menu == "🌍 Портал":
        choice = st.selectbox("Платформ сонгох", list(portals.keys()))
        st.components.v1.iframe(portals[choice], height=800, scrolling=True)
