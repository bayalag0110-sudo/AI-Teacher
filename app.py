import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# 1. API Түлхүүр тохиргоо (Secrets-ээс унших)
try:
    # Streamlit Secrets-ээс түлхүүрийг авна
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # Найдвартай ажиллах загварыг сонгох
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Secrets хэсэгт GOOGLE_API_KEY-ээ зөв оруулсан эсэхээ шалгана уу.")
    st.stop()

# 2. Вэб хуудасны дизайн
st.set_page_config(page_title="Ухаалаг Багшийн Туслах", page_icon="🎓")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #008080;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Word файл үүсгэх функц
def create_word_file(text, subject, topic):
    doc = Document()
    doc.add_heading('ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨГӨӨ', 0)
    doc.add_paragraph(f'Хичээл: {subject}')
    doc.add_paragraph(f'Сэдэв: {topic}')
    doc.add_heading('Төлөвлөгөө:', level=1)
    doc.add_paragraph(text)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# 4. Програмын үндсэн хэсэг
st.title("🎓 Ухаалаг Багшийн Туслах")
st.write("Орчин: Streamlit Cloud | AI: Gemini 1.5 Flash")

col1, col2 = st.columns(2)
with col1:
    subject = st.selectbox("📚 Хичээл", ["Математик", "Мэдээлэл технологи", "Монгол хэл", "Физик", "Биологи"])
    grade = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)])
with col2:
    topic = st.text_input("🔍 Хичээлийн сэдэв", placeholder="Жишээ: Мэдээлэл гэж юу вэ?")
    duration = st.slider("⏱️ Хугацаа (мин)", 20, 90, 40)

if st.button("✨ Хичээл төлөвлөгөө боловсруулах"):
    if not topic:
        st.warning("⚠️ Хичээлийн сэдвээ оруулна уу!")
    else:
        try:
            with st.spinner("🛠️ AI төлөвлөгөө боловсруулж байна..."):
                prompt = f"{subject} хичээлийн {grade}-д орох '{topic}' сэдвээр {duration} минутын хичээлийн төлөвлөгөөг Монгол хэл дээр маш тодорхой гаргаж өг."
                response = model.generate_content(prompt)
                full_plan = response.text
                
                st.markdown("---")
                st.markdown("### 📝 Боловсруулсан төлөвлөгөө")
                st.write(full_plan)
                
                # Word файлаар татах товч
                word_file = create_word_file(full_plan, subject, topic)
                st.download_button(
                    label="💾 Word файлаар татах",
                    data=word_file,
                    file_name=f"{topic}_plan.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        except Exception as e:
            st.error(f"Алдаа гарлаа: {e}")
