import streamlit as st
import requests
import datetime
from docx import Document
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Medle AI - Ухаалаг Багш", layout="wide", page_icon="🎓")

# 2. Статистик (Session State)
if 'plan_count' not in st.session_state: st.session_state.plan_count = 0
if 'teacher_emails' not in st.session_state: st.session_state.teacher_emails = set()

# 3. Нэвтрэх хэсэг
def login():
    st.sidebar.title("🔐 Багшийн нэвтрэх")
    email = st.sidebar.text_input("Эмайл (@medle.mn)")
    password = st.sidebar.text_input("Нууц үг", type="password")
    if st.sidebar.button("Нэвтрэх"):
        if email.strip().lower().endswith("@medle.mn") and password:
            st.session_state.logged_in = True
            st.session_state.user_email = email.strip().lower()
            st.session_state.teacher_emails.add(email.strip().lower())
            st.rerun()
        else:
            st.sidebar.error("❌ Зөвхөн @medle.mn хаяг зөвшөөрөгдөнө!")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🎓 Medle AI - Багшийн Систем")
    login()
    st.stop()

# 4. Үндсэн цэс
st.sidebar.success(f"👤 {st.session_state.user_email}")
menu = st.sidebar.selectbox("Цэс сонгох", 
    ["📖 Сурах бичгийн хуудаснаас бэлтгэх", "📝 Ээлжит хичээл төлөвлөх", "📊 ESIS", "🌐 Medle.mn", "🗺️ EduMap"])

# 5. ШИНЭ ФУНКЦ: СУРАХ БИЧГИЙН ХУУДАС ЗААЖ ӨГӨХ
if menu == "📖 Сурах бичгийн хуудаснаас бэлтгэх":
    st.title("📖 Сурах бичгийн агуулгаар боловсруулах")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📚 Сурах бичгийн мэдээлэл")
        book_link = st.text_input("Econtent сурах бичгийн линк:", "https://econtent.edu.mn/book/12bek/1")
        page_num = st.number_input("Ашиглах хуудасны дугаар:", min_value=1, value=1)
        
        # Сэдвээ гараар эсвэл AI-аар тодорхойлох
        topic_context = st.text_area("Тухайн хуудасны гол агуулга эсвэл сэдэв (Заавал биш):", 
                                     placeholder="Жишээ: 12-р ангийн Мэдээлэл зүй, Өгөгдлийн сангийн бүтэц")
        
        task_type = st.radio("Юу бэлтгэх вэ?", ["Ээлжит хичээлийн төлөвлөгөө", "5 минутын сорил"])
        
        if st.button("✨ Боловсруулж эхлэх"):
            with st.spinner("AI сурах бичгийн агуулгыг шинжилж байна..."):
                # Groq AI-д өгөх заавар
                prompt = f"""
                Econtent.edu.mn дээрх '{book_link}' сурах бичгийн {page_num}-р хуудсанд байх агуулгыг ашиглан {task_type} бэлтгэ.
                Хэрэв тухайн хуудас нь {topic_context} сэдэвтэй бол үүнийг анхаарна уу.
                
                Хичээлийн төлөвлөгөө бол: Эхлэл, Өрнөл, Төгсгөл хүснэгт хэлбэрээр.
                Сорил бол: 5 асуулттай, 4 сонголттой, зөв хариултын хамт.
                """
                
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                res = requests.post(url, headers=headers, json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}]
                })
                
                if res.status_code == 200:
                    st.session_state.plan_count += 1
                    st.session_state.current_result = res.json()['choices'][0]['message']['content']
                else:
                    st.error("Алдаа гарлаа. API Key эсвэл холболтоо шалгана уу.")

    with col2:
        st.subheader("🌐 Econtent Харагдац")
        # Сурах бичгийг хажууд нь нээж харуулах
        st.components.v1.iframe(book_link, height=600, scrolling=True)

    if 'current_result' in st.session_state:
        st.divider()
        st.subheader("📝 AI-аас бэлтгэсэн материал")
        st.markdown(st.session_state.current_result)
        
        # Word татах
        doc = Document()
        doc.add_heading(f"Сурах бичгийн {page_num}-р хуудаснаас бэлтгэсэн материал", 0)
        doc.add_paragraph(st.session_state.current_result)
        bio = BytesIO()
        doc.save(bio)
        st.download_button("📥 Word файлаар татах", bio.getvalue(), "Prepared_Material.docx")

# Бусад цэсүүд хэвээрээ...
elif menu == "📊 ESIS":
    st.components.v1.iframe("https://bagsh.esis.edu.mn/", height=800)
