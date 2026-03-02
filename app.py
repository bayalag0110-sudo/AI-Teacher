import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2
import gspread
from google.oauth2.service_account import Credentials

# 1. Хуудасны үндсэн тохиргоо
st.set_page_config(page_title="EduPlan Pro AI v2.7", layout="wide", page_icon="🎓")

# --- GOOGLE SHEETS ХОЛБОЛТЫН ФУНКЦ ---
def save_to_personal_sheet(sheet_id, doc_type, topic, content):
    try:
        # Secrets-ээс тохиргоо унших
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        
        # Багшийн оруулсан ID-гаар Sheet-ийг нээх
        sheet = client.open_by_key(sheet_id).sheet1
        
        # Өгөгдөл нэмэх (Огноо, Төрөл, Сэдэв, Агуулга)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        sheet.append_row([now, doc_type, topic, content])
        return True
    except Exception as e:
        st.error(f"Хадгалахад алдаа гарлаа: {e}")
        return False

# --- CUSTOM CSS ---
if 'theme' not in st.session_state: st.session_state.theme = 'light'
curr_theme = {
    'light': {'bg': 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)', 'card': 'rgba(255, 255, 255, 0.8)', 'text': '#0f172a'},
    'dark': {'bg': 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', 'card': 'rgba(30, 41, 59, 0.7)', 'text': '#f8fafc'}
}
curr = curr_theme[st.session_state.theme]

st.markdown(f"""
    <style>
    .stApp {{ background-image: {curr['bg']}; color: {curr['text']}; }}
    .glass-card {{ background: {curr['card']}; backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px; }}
    .main-title {{ text-align: center; color: #2563eb; font-weight: 800; font-size: 2.5rem; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Нууц үг:", type="password")
        if st.button("Нэвтрэх"):
            if pwd == "admin1234": st.session_state.authenticated = True; st.rerun()
            else: st.error("Буруу!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR: ХУВИЙН ТОХИРГОО ---
with st.sidebar:
    st.markdown("### ⚙️ Багшийн тохиргоо")
    teacher_name = st.text_input("Багшийн нэр:", value="Б. Багш")
    personal_sheet_id = st.text_input("Google Sheet ID:", help="Өөрийн Sheet-ийн URL-аас ID-г хуулж тавина уу.")
    st.info("💡 Та өөрийн Sheet-ээ системийн мэйл хаягт (Service Account) 'Editor' эрхтэйгээр Share хийсэн байх шаардлагатай.")
    
    if st.button("🌓 Горим солих"):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'; st.rerun()
    
    menu = st.radio("ЦЭС", ["💎 Төлөвлөгч", "📝 Тест үүсгэгч", "📊 Миний сан", "🌍 Портал"])
    if st.button("🚪 Гарах"): st.session_state.authenticated = False; st.rerun()

# --- 1. ТӨЛӨВЛӨГЧ ---
if menu == "💎 Төлөвлөгч":
    st.markdown("<h1 class='main-title'>Ээлжит хичээл төлөвлөлт</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        file = st.file_uploader("PDF оруулах", type="pdf")
        l_type = st.selectbox("Төрөл", ["Шинэ мэдлэг", "Батгах", "Дадлага"])
        tpc = st.text_input("Сэдэв")
        if st.button("🚀 Боловсруулах"):
            if file and tpc:
                with st.spinner("AI ажиллаж байна..."):
                    reader = PyPDF2.PdfReader(file)
                    txt = "".join([p.extract_text() for p in reader.pages[:10]])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"Сэдэв: {tpc}, Төрөл: {l_type}. Энэ сэдвээр 45 минутын төлөвлөгөө гарга. Агуулга: {txt[:4000]}"
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    if res.status_code == 200:
                        content = res.json()['choices'][0]['message']['content']
                        st.session_state.curr_plan = content
                        if personal_sheet_id:
                            save_to_personal_sheet(personal_sheet_id, "Төлөвлөгөө", tpc, content)
                            st.success("✅ Таны Google Drive-д хадгалагдлаа!")
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'curr_plan' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.curr_plan); st.markdown('</div>', unsafe_allow_html=True)

# --- 2. ТЕСТ ҮҮСГЭГЧ ---
elif menu == "📝 Тест үүсгэгч":
    st.markdown("<h1 class='main-title'>Тест үүсгэгч</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t_file = st.file_uploader("PDF оруулах", type="pdf", key="t_up")
        s_p = st.number_input("Эхлэх хуудас", 1); e_p = st.number_input("Дуусах хуудас", 5)
        t_tpc = st.text_input("Сэдэв")
        if st.button("🎯 Тест үүсгэх"):
            if t_file and t_tpc:
                with st.spinner("Тест бэлдэж байна..."):
                    reader = PyPDF2.PdfReader(t_file)
                    t_txt = "".join([reader.pages[i].extract_text() for i in range(s_p-1, min(e_p, len(reader.pages)))])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"Текстэд тулгуурлан {t_tpc} сэдвээр тест бэлд. Текст: {t_txt[:6000]}"
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1})
                    if res.status_code == 200:
                        content = res.json()['choices'][0]['message']['content']
                        st.session_state.curr_test = content
                        if personal_sheet_id:
                            save_to_personal_sheet(personal_sheet_id, "Тест", t_tpc, content)
                            st.success("✅ Таны Google Drive-д хадгалагдлаа!")
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'curr_test' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.curr_test); st.markdown('</div>', unsafe_allow_html=True)

# --- 3. МИНИЙ САН (CLOUD READ) ---
elif menu == "📊 Миний сан":
    st.markdown("<h1 class='main-title'>Миний Google Drive сан</h1>", unsafe_allow_html=True)
    if not personal_sheet_id:
        st.warning("⚠️ Sidebar-д өөрийн Google Sheet ID-г оруулж холбоно уу.")
    else:
        try:
            scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
            client = gspread.authorize(creds)
            sheet = client.open_by_key(personal_sheet_id).sheet1
            data = sheet.get_all_records()
            if not data: st.info("Сан хоосон байна.")
            else:
                for item in reversed(data):
                    with st.expander(f"📅 {item.get('now', 'Үл мэдэгдэх')} | 📌 {item.get('doc_type', 'Төрөл')}: {item.get('topic', 'Сэдэв')}"):
                        st.markdown(item.get('content', 'Хоосон'))
        except: st.error("Sheet ID буруу эсвэл эрх өгөөгүй байна.")

# --- 4. ПОРТАЛ ---
elif menu == "🌍 Портал":
    st.markdown("<h2 class='main-title'>Боловсролын порталууд</h2>", unsafe_allow_html=True)
    tabs = st.tabs(["📚 E-Content", "👨‍🏫 Bagsh.edu.mn", "✅ Үнэлгээ (eec.mn)", "📊 EEC Мэдээлэл"])
    with tabs[0]: components.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)
    with tabs[1]: components.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)
    with tabs[2]: components.iframe("https://unelgee.eec.mn/", height=800, scrolling=True)
    with tabs[3]: components.iframe("https://www.eec.mn/post/5891", height=800, scrolling=True)
