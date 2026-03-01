import streamlit as st
import requests
import datetime
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2
import plotly.express as px # Анализ хийхэд ашиглана

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="EduPlan AI - Pro", layout="wide", page_icon="🎓")

# --- МЭДЭЭЛЛИЙН САН (Simple Database Simulation) ---
# Жич: Бодит хэрэглээнд SQL Database ашиглах нь тохиромжтой
if 'user_db' not in st.session_state:
    st.session_state.user_db = {"admin": "admin123"} # Анхны хэрэглэгч

# 2. НЭВТРЭХ БА БҮРТГЭХ ЛОГИК
def auth_system():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = ""

    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align: center;'>🔐 EduPlan AI систем</h2>", unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["Нэвтрэх", "Бүртгүүлэх"])
        
        with tab_login:
            user_in = st.text_input("Хэрэглэгчийн нэр", key="login_user")
            pass_in = st.text_input("Нууц үг", type="password", key="login_pass")
            if st.button("Нэвтрэх"):
                if user_in in st.session_state.user_db and st.session_state.user_db[user_in] == pass_in:
                    st.session_state.authenticated = True
                    st.session_state.username = user_in
                    st.rerun()
                else:
                    st.error("Нэр эсвэл нууц үг буруу байна.")
        
        with tab_signup:
            new_user = st.text_input("Шинэ нэр", key="reg_user")
            new_pass = st.text_input("Шинэ нууц үг", type="password", key="reg_pass")
            confirm_pass = st.text_input("Нууц үг давтах", type="password", key="reg_confirm")
            if st.button("Бүртгүүлэх"):
                if new_user in st.session_state.user_db:
                    st.warning("Энэ нэр бүртгэлтэй байна.")
                elif new_pass != confirm_pass:
                    st.error("Нууц үг зөрүүтэй байна.")
                elif new_user and new_pass:
                    st.session_state.user_db[new_user] = new_pass
                    st.success("Амжилттай бүртгэгдлээ. Одоо Нэвтрэх таб руу орно уу.")
        return False
    return True

if auth_system():
    # 3. CSS & ХУУДАСНЫ БҮТЭЦ
    st.markdown("""
        <style>
        .portal-link { padding: 10px; border-radius: 5px; background-color: #f0f2f6; border-left: 5px solid #28a745; margin-bottom: 5px; display: block; text-decoration: none; color: #31333F; font-weight: bold; }
        .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        </style>
        """, unsafe_allow_html=True)

    if 'history' not in st.session_state: st.session_state.history = []

    # 4. SIDEBAR
    with st.sidebar:
        st.title(f"👤 {st.session_state.username}")
        if st.button("🚪 Гарах"):
            st.session_state.authenticated = False
            st.rerun()
        
        st.divider()
        menu = st.radio("Цэс", ["Хичээл боловсруулах", "Миний Анализ", "Портал сайтууд"])
        
        st.divider()
        st.subheader("🕒 Сүүлийн түүх")
        for idx, item in enumerate(st.session_state.history[-5:]): # Сүүлийн 5
            st.caption(f"📄 {item['topic']} ({item['date']})")

    # 5. АНАЛИЗ ХЭСЭГ (DASHBOARD)
    if menu == "Миний Анализ":
        st.header("📊 Хичээл боловсруулалтын анализ")
        
        if not st.session_state.history:
            st.info("Анализ хийх мэдээлэл хараахан алга. Эхлээд хичээл боловсруулна уу.")
        else:
            df = pd.DataFrame(st.session_state.history)
            
            # Үзүүлэлтүүд
            c1, c2, c3 = st.columns(3)
            c1.metric("Нийт боловсруулсан", len(df))
            c2.metric("Сүүлийн хичээл", df.iloc[-1]['topic'])
            c3.metric("Хамгийн их орсон анги", df['grd'].mode()[0] if not df['grd'].empty else "-")

            st.divider()
            
            # График 1: Ангиар
            fig_grd = px.pie(df, names='grd', title="Боловсруулсан хичээлүүд (Ангиар)")
            st.plotly_chart(fig_grd, use_container_width=True)

    # 6. ХИЧЭЭЛ БОЛОВСРУУЛАХ ХЭСЭГ
    elif menu == "Хичээл боловсруулах":
        st.header("👨‍🏫 Ээлжит хичээл боловсруулах")
        
        col_in, col_out = st.columns([1, 1.2])
        
        with col_in:
            uploaded_file = st.file_uploader("Сурах бичгийн PDF оруулна уу", type="pdf")
            sub = st.text_input("Хичээл", "Мэдээлэл зүй")
            grd = st.selectbox("Анги", ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])
            tpc = st.text_input("Хичээлийн сэдэв")
            
            if st.button("🚀 Боловсруулах"):
                if uploaded_file and tpc:
                    with st.spinner("AI шинжилж байна..."):
                        # PDF Унших
                        pdf_reader = PyPDF2.PdfReader(uploaded_file)
                        pdf_text = "".join([page.extract_text() for page in pdf_reader.pages])
                        
                        # API Хүсэлт
                        url = "https://api.groq.com/openai/v1/chat/completions"
                        headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                        
                        system_prompt = """Чи бол Монгол улсын Боловсролын шинжээч багш. 
                        Зөвхөн өгөгдсөн PDF-д тулгуурлан 'ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ.docx' загвараар, 70/30 харьцаатай төлөвлөгөө гарга. 
                        Юу ч битгий зохио. Temperature 0.1."""
                        
                        payload = {
                            "model": "llama-3.3-70b-versatile",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": f"Сэдэв: {tpc}\nТекст: {pdf_text[:8000]}"}
                            ],
                            "temperature": 0.1
                        }
                        
                        res = requests.post(url, headers=headers, json=payload)
                        if res.status_code == 200:
                            ans = res.json()['choices'][0]['message']['content']
                            now = datetime.datetime.now()
                            
                            # Түүхэнд хадгалах
                            new_entry = {
                                "topic": tpc, "sub": sub, "grd": grd, 
                                "content": ans, "date": now.strftime("%Y-%m-%d"),
                                "time": now.strftime("%H:%M")
                            }
                            st.session_state.history.append(new_entry)
                            st.session_state.current_view = new_entry
                            st.rerun()

        with col_out:
            if 'current_view' in st.session_state and st.session_state.current_view:
                item = st.session_state.current_view
                st.info(f"Сэдэв: {item['topic']}")
                st.markdown(item['content'])
                
                # Word Export
                doc = Document()
                doc.add_paragraph(item['content'])
                bio = BytesIO()
                doc.save(bio)
                st.download_button("📥 Word татах", bio.getvalue(), f"{item['topic']}.docx")
            else:
                st.info("👈 PDF файлаа оруулж, сэдвээ бичнэ үү.")

    # 7. ПОРТАЛ ХЭСЭГ
    elif menu == "Портал сайтууд":
        st.header("🌐 Сургалтын платформ")
        portals = {
            "Econtent": "https://econtent.edu.mn/book",
            "Medle": "https://medle.mn/",
            "EduMap": "https://edumap.mn/"
        }
        choice = st.selectbox("Сайт сонгох", list(portals.keys()))
        st.components.v1.iframe(portals[choice], height=800, scrolling=True)
