import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2

# 1. Хуудасны үндсэн тохиргоо
st.set_page_config(page_title="EduPlan Pro AI v2.6", layout="wide", page_icon="🎓")

# --- СИСТЕМИЙН САНГ ЭХЛҮҮЛЭХ (Storage) ---
if 'my_vault' not in st.session_state:
    st.session_state.my_vault = [] # Төлөвлөгөө болон тестүүдийг хадгалах жагсаалт

# --- CUSTOM CSS ---
if 'theme' not in st.session_state: st.session_state.theme = 'light'
theme_css = {
    'light': {'bg': 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #bae6fd 100%)', 'card': 'rgba(255, 255, 255, 0.75)', 'text': '#0f172a'},
    'dark': {'bg': 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)', 'card': 'rgba(30, 41, 59, 0.7)', 'text': '#f8fafc'}
}
curr = theme_css[st.session_state.theme]

st.markdown(f"""
    <style>
    .stApp {{ background-image: {curr['bg']}; color: {curr['text']}; }}
    .glass-card {{ background: {curr['card']}; backdrop-filter: blur(12px); border-radius: 20px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1); margin-bottom: 20px; }}
    .main-title {{ text-align: center; background: linear-gradient(to right, #2563eb, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 2.8rem; margin-bottom: 1rem; }}
    .stButton>button {{ border-radius: 12px; background: linear-gradient(45deg, #2563eb, #7c3aed); color: white; border: none; padding: 12px 24px; width: 100%; font-weight: bold; transition: 0.3s ease; }}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
components.html(f"""
<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 30px; border-radius: 20px; text-align: center; color: white; font-family: 'Poppins', sans-serif;">
    <h1 style="margin:0; font-size: 2.2rem;">🌊 EDUPLAN PRO AI</h1>
    <p style="opacity: 0.9;">Боловсролын нэгдсэн систем v2.6</p>
</div>
""", height=180)

# --- LOGIN LOGIC ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Нууц үг:", type="password")
        if st.button("Нэвтрэх"):
            if pwd == "admin1234":
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("❌ Нууц үг буруу!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ✨ Цэс")
    if st.button("🌓 Горим солих"):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()
    menu = st.radio("ШИЛЖИХ", ["💎 Төлөвлөгч", "📝 Тест үүсгэгч", "📊 Миний сан", "🌍 Портал"])
    if st.button("🚪 Гарах"):
        st.session_state.authenticated = False
        st.rerun()

# --- 1. ТӨЛӨВЛӨГЧ ---
if menu == "💎 Төлөвлөгч":
    st.markdown("<h1 class='main-title'>Хичээл төлөвлөлт</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.6])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        file = st.file_uploader("Сурах бичиг (PDF)", type="pdf")
        l_type = st.selectbox("Төрөл", ["Шинэ мэдлэг", "Батгах", "Дадлага", "Шалгалт"])
        tpc = st.text_input("Сэдэв")
        if st.button("🚀 Боловсруулах"):
            if file and tpc:
                with st.spinner("AI ажиллаж байна..."):
                    reader = PyPDF2.PdfReader(file)
                    txt = "".join([p.extract_text() for p in reader.pages[:10]])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"БАТЛАВ: МЕНЕЖЕР Б. НАМУУН\nТөрөл: {l_type}\nСэдэв: {tpc}\nАгуулга: {txt[:5000]}\nТөлөвлөгөө гарга."
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    if res.status_code == 200:
                        content = res.json()['choices'][0]['message']['content']
                        st.session_state.current_plan = content
                        # САНД ХАДГАЛАХ
                        st.session_state.my_vault.append({"type": "Төлөвлөгөө", "topic": tpc, "date": str(datetime.date.today()), "content": content})
                        st.success("✅ Санд хадгалагдлаа!")
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'current_plan' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.current_plan)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 2. ТЕСТ ҮҮСГЭГЧ ---
elif menu == "📝 Тест үүсгэгч":
    st.markdown("<h1 class='main-title'>Тест үүсгэгч</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.6])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t_file = st.file_uploader("PDF оруулах", type="pdf")
        st.write("📖 Хуудас:")
        c1, c2 = st.columns(2); s_p = c1.number_input("Эхлэх", 1); e_p = c2.number_input("Дуусах", 5)
        t_tpc = st.text_input("Тестийн сэдэв")
        t_format = st.multiselect("Хэлбэр", ["Нэг сонголттой", "Олон хариулттай", "Нөхөх", "Зөв/Буруу"], default=["Нэг сонголттой"])
        if st.button("🎯 Тест үүсгэх"):
            if t_file and t_tpc:
                with st.spinner("Тест бэлдэж байна..."):
                    reader = PyPDF2.PdfReader(t_file)
                    t_txt = "".join([reader.pages[i].extract_text() for i in range(s_p-1, min(e_p, len(reader.pages)))])
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"Текстэд тулгуурлан {t_tpc} сэдвээр тест бэлд. Хэлбэр: {t_format}. Текст: {t_txt[:6000]}"
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1})
                    if res.status_code == 200:
                        content = res.json()['choices'][0]['message']['content']
                        st.session_state.generated_test = content
                        # САНД ХАДГАЛАХ
                        st.session_state.my_vault.append({"type": "Тест", "topic": t_tpc, "date": str(datetime.date.today()), "content": content})
                        st.success("✅ Санд хадгалагдлаа!")
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if 'generated_test' in st.session_state:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.generated_test)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 3. МИНИЙ САН (ШИНЭЧЛЭГДСЭН) ---
elif menu == "📊 Миний сан":
    st.markdown("<h1 class='main-title'>Миний сан</h1>", unsafe_allow_html=True)
    if not st.session_state.my_vault:
        st.info("Одоогоор хадгалсан файл байхгүй байна. Төлөвлөгөө эсвэл Тест үүсгэсний дараа энд автоматаар хадгалагдана.")
    else:
        for idx, item in enumerate(reversed(st.session_state.my_vault)):
            with st.expander(f"📅 {item['date']} | 📌 {item['type']}: {item['topic']}"):
                st.markdown(item['content'])
                doc = Document(); doc.add_paragraph(item['content'])
                bio = BytesIO(); doc.save(bio)
                st.download_button(f"📥 Word татах ({idx})", bio.getvalue(), f"{item['topic']}.docx", key=f"dl_{idx}")

# --- 4. ПОРТАЛ (ШИНЭЧЛЭГДСЭН) ---
elif menu == "🌍 Портал":
    st.markdown("<h2 class='main-title'>Боловсролын порталууд</h2>", unsafe_allow_html=True)
    tabs = st.tabs(["📚 E-Content", "💻 Medle.mn", "👨‍🏫 Bagsh.edu.mn", "✅ Үнэлгээ (unelgee.eec.mn)", "📊 EEC Мэдээлэл"])
    with tabs[0]: components.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)
    with tabs[1]: components.iframe("https://medle.mn/", height=800, scrolling=True)
    with tabs[2]: components.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)
    with tabs[3]: components.iframe("https://unelgee.eec.mn/", height=800, scrolling=True)
    with tabs[4]: components.iframe("https://www.eec.mn/post/5891", height=800, scrolling=True)
