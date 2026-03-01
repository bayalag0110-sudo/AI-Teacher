import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# 1. Gemini AI Тохиргоо (Secrets-ээс унших)
# Streamlit Cloud-ийн Settings -> Secrets хэсэгт GOOGLE_API_KEY-ээ хийнэ.
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    # Хэрэв локал дээр ажиллуулж байгаа бол доорх хашилтан дотор Key-ээ хийж болно
    api_key = "AIzaSyD-qC9TwkdOxl38icULTJ4BHzVTMNoPvTA"

def setup_model():
    try:
        genai.configure(api_key=api_key)
        # 404 алдаанаас сэргийлж хэд хэдэн хувилбарыг турших
        models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        for model_name in models_to_try:
            try:
                m = genai.GenerativeModel(model_name)
                # Холболтыг шалгах тест
                m.generate_content("test", generation_config={"max_output_tokens": 1})
                return m
            except:
                continue
        return None
    except Exception as e:
        st.error(f"Тохиргооны алдаа: {e}")
        return None

model = setup_model()

# 2. Вэб дизайны тохиргоо
st.set_page_config(page_title="Ухаалаг Багшийн Туслах", page_icon="🎓")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background-color: #008080;
        color: white;
        height: 3.5em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Word файл үүсгэх функц
def create_word_file(text, subject, topic):
    doc = Document()
    doc.add_heading('ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨГӨӨ', 0)
    doc.add_paragraph(f'Хичээл: {subject}\nСэдэв: {topic}')
    doc.add_heading('Төлөвлөгөө:', level=1)
    doc.add_paragraph(text)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# 4. Программ
st.title("🎓 Ухаалаг Багшийн Туслах")
st.info("Хичээлийн төлөвлөгөө боловсруулах систем")

col1, col2 = st.columns(2)
with col1:
    subject = st.selectbox("📚 Хичээл", ["Математик", "Монгол хэл", "Мэдээлэл технологи", "Биологи", "Физик", "Бусад"])
    grade = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)])
with col2:
    topic = st.text_input("🔍 Хичээлийн сэдэв", placeholder="Сэдвээ бичнэ үү...")
    duration = st.slider("⏱️ Хугацаа (мин)", 20, 90, 40)

if st.button("✨ Төлөвлөгөө боловсруулах"):
    if not topic:
        st.warning("⚠️ Сэдвээ оруулна уу!")
    elif model is None:
        st.error("❌ AI Модельтой холболт тогтоож чадсангүй. Secrets хэсэгт API Key-ээ зөв оруулсан эсэхээ шалгана уу.")
    else:
        try:
            with st.spinner("🛠️ AI ажиллаж байна..."):
                prompt = f"{subject} хичээлийн {grade}-д орох '{topic}' сэдвээр {duration} минутын хичээлийн төлөвлөгөөг маш тодорхой гаргаж өг."
                response = model.generate_content(prompt)
                full_plan = response.text
                
                st.markdown("### 📝 Боловсруулсан төлөвлөгөө")
                st.write(full_plan)
                
                word_file = create_word_file(full_plan, subject, topic)
                st.download_button(
                    label="💾 Word файлаар татах",
                    data=word_file,
                    file_name=f"{topic}_plan.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        except Exception as e:
            st.error(f"Алдаа гарлаа: {e}")


