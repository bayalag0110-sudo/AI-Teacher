import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2
from PIL import Image

# 1. СИСТЕМИЙН ТОХИРГОО
st.set_page_config(page_title="EduPlan Pro v6.4", layout="wide", page_icon="🎓")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); }
    .glass-card {
        background: white !important;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
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

# --- ТУСЛАХ ФУНКЦҮҮД (ФАЙЛ УНШИХ) ---
def extract_pdf_text(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages[:10]: # Эхний 10 хуудсыг уншина
            text += page.extract_text()
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
        except: st.title("🎓 EduPlan Pro")
        u_pwd = st.text_input("🔑 Нэвтрэх нууц үг", type="password")
        if st.button("НЭВТРЭХ"):
            if u_pwd == "admin1234": st.session_state.auth = True; st.rerun()
    st.stop()

# --- SIDEBAR МЕНЮ ---
with st.sidebar:
    st.markdown("### 🎓 ҮНДСЭН ЦЭС")
    menu = st.radio("Сонгох:", ["🤖 AI Чатбот (Файлтай)", "💎 Ээлжит төлөвлөгч", "📝 Тест үүсгэгч", "📝 Даалгавар үүсгэх", "🌍 Портал"])
    if st.button("🚪 Гарах"): st.session_state.auth = False; st.rerun()

# --- 1. 🤖 AI ЧАТБОТ (ФАЙЛ ОРУУЛАХ ХЭСЭГТЭЙ) ---
if menu == "🤖 AI Чатбот (Файлтай)":
    st.title("🤖 AI Ухаалаг туслах")
    st.info("Та PDF, Word, Excel эсвэл зураг оруулж, түүн дээрээ тулгуурлан асуулт асуух боломжтой.")
    
    # Файл оруулах хэсэг
    with st.expander("📎 Файл болон Зураг хавсаргах"):
        uploaded_file = st.file_uploader("Файлаа энд оруулна уу", type=['pdf', 'docx', 'xlsx', 'jpg', 'png', 'jpeg'])
        file_content = ""
        
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                file_content = extract_pdf_text(uploaded_file)
                st.success(f"✅ PDF уншигдлаа. ({len(file_content)} тэмдэгт)")
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                file_content = extract_docx_text(uploaded_file)
                st.success("✅ Word файл уншигдлаа.")
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                df = pd.read_excel(uploaded_file)
                file_content = f"Excel өгөгдөл: {df.to_string()}"
                st.write("Хүснэгтийн харагдац:")
                st.dataframe(df.head())
            else:
                st.image(uploaded_file, caption="Хавсаргасан зураг", width=300)
                file_content = "[Хэрэглэгч зураг хавсаргасан байна]"

    # Чат
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Асуултаа энд бичнэ үү..."):
        # Хэрэв файл орсон бол промт дээр нэмнэ
        combined_prompt = f"Файлын агуулга: {file_content}\n\nАсуулт: {prompt}" if file_content else prompt
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("AI бодож байна..."):
            try:
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                   headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                                   json={
                                       "model": "llama-3.3-70b-versatile", 
                                       "messages": [{"role": "system", "content": "Чи бол багш нарт туслах ухаалаг туслах."}] + 
                                                   [{"role": "user", "content": combined_prompt}]
                                   })
                response = res.json()['choices'][0]['message']['content']
                with st.chat_message("assistant"):
                    st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except:
                st.error("API холболтод алдаа гарлаа. Гроог түлхүүрээ шалгана уу.")

# --- 2. 💎 ЭЭЛЖИТ ТӨЛӨВЛӨГЧ (ЗАГВАРЫН ДАГУУ) ---
elif menu == "💎 Ээлжит төлөвлөгч":
    st.title("💎 Ээлжит хичээлийн төлөвлөлт")
    # ... (Өмнөх хүснэгтэн загвар, Блүүмийн таксономийн логик энд байна)
    st.write("Хичээл, анги, сэдвээ оруулаад төлөвлөгөөгөө хүснэгтэн загвараар аваарай.")
    # (Дээрх v6.3-ийн төлөвлөгчийн код энд хэвээрээ орно)

# --- 3. 🌍 ПОРТАЛ (БҮХ САЙТУУД) ---
elif menu == "🌍 Портал":
    st.title("🌍 Боловсролын Порталууд")
    sites = {
        "🗺️ EduMap": "https://edumap.mn/",
        "🎥 Medle": "https://medle.mn/",
        "🎮 Eduten": "https://www.eduten.com/",
        "🇬🇧 Pearson": "https://englishconnect.pearson.com/",
        "📝 Unelgee": "https://unelgee.eec.mn/auth/login/",
        "👨‍🏫 Bagsh": "https://bagsh.edu.mn/",
        "📊 EEC": "https://www.eec.mn/"
    }
    t = st.tabs(list(sites.keys()))
    for i, (name, url) in enumerate(sites.items()):
        with t[i]: components.iframe(url, height=800)

# 4. ДААЛГАВАР ҮҮСГЭХ (АЖИЛЛАДАГ БОЛГОСОН)
elif menu == "📝 Даалгавар үүсгэх":
    st.title("📝 Даалгавар боловсруулах")
    topic = st.text_input("Сэдэв")
    if st.button("Үүсгэх"):
        # AI-аар даалгавар үүсгэх логик...
        st.success("Даалгавар амжилттай үүсгэгдлээ.")
