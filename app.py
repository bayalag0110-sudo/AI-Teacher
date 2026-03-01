import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# 1. Gemini AI Тохиргоо
# ШИНЭ API KEY-ЭЭ ДООРХ ХАШИЛТ ДОТОР ХУУЛЖ НААГААРАЙ
GOOGLE_API_KEY = "AIzaSyAca_6vZqN9r2Dl5sSehXe2_LmD_uN1nsI"

def setup_model():
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Python 3.14 дээр 404 алдаанаас сэргийлэх дараалал
        # Эхлээд Flash, болохгүй бол Pro-г туршина
        models_to_try = [
            'gemini-1.5-flash-latest', 
            'gemini-1.5-flash', 
            'gemini-pro'
        ]
        
        for model_name in models_to_try:
            try:
                m = genai.GenerativeModel(model_name)
                # Жижиг тест хийж холболтыг шалгах
                m.generate_content("ping", generation_config={"max_output_tokens": 1})
                return m
            except:
                continue
        return None
    except Exception as e:
        st.error(f"Тохиргооны алдаа: {e}")
        return None

# Моделийг ачаалах
model = setup_model()

# 2. Дизайн болон CSS
st.set_page_config(page_title="Ухаалаг Багш", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #00796b;
        color: white;
        font-weight: bold;
        border: none;
    }
    .lesson-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Word файл үүсгэх функц
def create_word_file(text, subject, topic):
    doc = Document()
    doc.add_heading('ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨГӨӨ', 0)
    doc.add_paragraph(f'Хичээл: {subject}')
    doc.add_paragraph(f'Сэдэв: {topic}')
    doc.add_heading('Төлөвлөгөөний дэлгэрэнгүй', level=1)
    doc.add_paragraph(text)
    
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# 4. Программ
st.title("🎓 Ухаалаг Багшийн Туслах")
st.write(f"Орчин: Python 3.14.3 | Gemini AI")

st.markdown('<div class="lesson-card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    subject = st.selectbox("📚 Хичээл", ["Математик", "Монгол хэл", "Биологи", "Физик", "Мэдээлэл технологи", "Хими", "Англи хэл", "Бусад"])
    grade = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)])
with col2:
    topic = st.text_input("🔍 Хичээлийн сэдэв", placeholder="Жишээ: Нарны систем")
    duration = st.select_slider("⏱️ Хугацаа (мин)", options=[20, 35, 40, 45, 80, 90], value=40)
st.markdown('</div>', unsafe_allow_html=True)

# 5. AI Ажиллуулах
if st.button("✨ Хичээл төлөвлөгөөг боловсруулах"):
    if not topic:
        st.warning("⚠️ Сэдвээ оруулна уу!")
    elif model is None:
        st.error("❌ AI Модельтой холбогдож чадсангүй. API Key эсвэл бүс нутгийн хязгаарлалт байж магадгүй.")
    else:
        try:
            with st.status("🛠️ AI төлөвлөгөө гаргаж байна...", expanded=True) as status:
                prompt = f"""
                Чи бол Монголын ЕБС-ийн туршлагатай багш юм. 
                Дараах мэдээллээр хичээлийн төлөвлөгөө гарга:
                Хичээл: {subject}, Анги: {grade}, Сэдэв: {topic}, Хугацаа: {duration} минут.
                Бүтэц: Зорилго, Суралцахуйн зорилт, Хичээлийн явц (Хүснэгтээр), Үнэлгээ.
                Хариултыг Монгол хэлээр өг.
                """
                
                response = model.generate_content(prompt)
                full_plan = response.text
                status.update(label="✅ Төлөвлөгөө бэлэн боллоо!", state="complete", expanded=False)

            st.markdown("### 📝 Боловсруулсан төлөвлөгөө")
            st.markdown(full_plan)
            
            # Word татах
            word_file = create_word_file(full_plan, subject, topic)
            st.download_button(
                label="💾 Word файлаар татах",
                data=word_file,
                file_name=f"{topic}_plan.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Алдаа гарлаа: {e}")