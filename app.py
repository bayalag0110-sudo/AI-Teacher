import streamlit as st
import requests
import datetime
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# 1. Хуудасны тохиргоо (Wide mode нь хоёр талбарт хуваахад тохиромжтой)
st.set_page_config(page_title="Medle AI - Багшийн Төв", layout="wide", page_icon="🎓")

# 2. Статистик (Session State)
if 'plan_count' not in st.session_state:
    st.session_state.plan_count = 0
if 'teacher_emails' not in st.session_state:
    st.session_state.teacher_emails = set()

# 3. Нэвтрэх хэсэг
def login():
    st.sidebar.title("🔐 Нэвтрэх")
    email = st.sidebar.text_input("Эмайл (@medle.mn)")
    password = st.sidebar.text_input("Нууц үг", type="password")
    if st.sidebar.button("Системд нэвтрэх"):
        if email.strip().lower().endswith("@medle.mn") and password:
            st.session_state.logged_in = True
            st.session_state.user_email = email.strip().lower()
            st.session_state.teacher_emails.add(email.strip().lower())
            st.rerun()
        else:
            st.sidebar.error("❌ Зөвхөн @medle.mn хаягаар нэвтэрнэ!")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🎓 Medle AI - Ухаалаг Багшийн Систем")
    c1, c2 = st.columns(2)
    with c1: st.metric("Нийт боловсруулсан хичээл", st.session_state.plan_count)
    with c2: st.metric("Идэвхтэй багш нар", len(st.session_state.teacher_emails))
    login()
    st.stop()

# 4. Үндсэн цэс (Нэвтэрсний дараа)
st.sidebar.success(f"👤 {st.session_state.user_email}")
menu = st.sidebar.radio("Цэс", ["Ээлжит хичээл төлөвлөх", "Сурах бичиг (Econtent)", "Medle.mn сайт"])
if st.sidebar.button("Системээс гарах"):
    st.session_state.logged_in = False
    st.rerun()

# 5. Хичээл төлөвлөх хэсэг
if menu == "Ээлжит хичээл төлөвлөх":
    st.title("📝 Ээлжит хичээлийн төлөвлөлт")
    
    col1, col2 = st.columns([1, 1]) # Дэлгэцийг хоёр хуваах
    
    with col1:
        st.subheader("⚙️ Тохиргоо")
        sub = st.text_input("Хичээлийн нэр", "Мэдээлэл зүй")
        grd = st.selectbox("Анги", [f"{i}-р анги" for i in range(1, 13)])
        tpc = st.text_input("Ээлжит хичээлийн сэдэв")
        dur = st.number_input("Хугацаа (минут)", 40)
        
        if st.button("✨ Төлөвлөгөө боловсруулах"):
            if tpc:
                with st.spinner("AI боловсруулж байна..."):
                    # Groq API дуудах хэсэг (Llama 3.3)
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    prompt = f"Монгол улсын ээлжит хичээлийн төлөвлөлтийн загвараар {sub} хичээлийн {grd}-ийн '{tpc}' сэдвийг Эхлэл, Өрнөл, Төгсгөл үе шаттай, хүснэгт хэлбэрээр боловсруулж өг."
                    
                    res = requests.post(url, headers=headers, json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}]
                    })
                    
                    if res.status_code == 200:
                        st.session_state.plan_count += 1
                        st.session_state.last_result = res.json()['choices'][0]['message']['content']
                    else:
                        st.error("AI холболтод алдаа гарлаа.")

    with col2:
        st.subheader("📄 Төлөвлөгөөний харагдац")
        if 'last_result' in st.session_state:
            st.markdown(st.session_state.last_result)
            
            # Word файл татах
            doc = Document()
            doc.add_heading('ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ', 0)
            doc.add_paragraph(st.session_state.last_result)
            bio = BytesIO()
            doc.save(bio)
            st.download_button("📥 Word татах", bio.getvalue(), f"{tpc}.docx")

# 6. E-Content хэсэг (iframe ашиглан сайт оруулах)
elif menu == "Сурах бичиг (Econtent)":
    st.title("📚 Цахим сурах бичиг")
    st.components.v1.iframe("https://econtent.edu.mn/book", height=800, scrolling=True)

# 7. Medle.mn хэсэг
elif menu == "Medle.mn сайт":
    st.title("🌐 Medle.mn Портал")
    st.components.v1.iframe("https://medle.mn/", height=800, scrolling=True)
