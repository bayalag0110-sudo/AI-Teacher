import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# 1. СҮҮЛИЙН ҮЕИЙН ТОГТВОРТОЙ ТОХИРГОО
try:
    # Secrets-ээс шинэ түлхүүрийг унших
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        st.error("Streamlit Cloud-ийн Secrets хэсэгт GOOGLE_API_KEY-ээ оруулна уу.")
        st.stop()

    # REST тээвэрлэлтийг ашиглан 404 алдаанаас сэргийлэх
    genai.configure(api_key=api_key, transport='rest')
    
    # Хамгийн сүүлийн үеийн тогтвортой моделийг сонгох
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Тохиргооны алдаа: {e}")
    st.stop()

# 2. ВЭБ САЙТЫН ДИЗАЙН
st.set_page_config(page_title="Ухаалаг Багшийн Туслах", page_icon="🎓")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #008080;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    .main {
        background-color: #f5f7f9;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. WORD ФАЙЛ ҮҮСГЭХ ФУНКЦ
def create_word_file(text, subject, topic):
    doc = Document()
    doc.add_heading('ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨГӨӨ', 0)
    doc.add_paragraph(f'📚 Хичээл: {subject}')
    doc.add_paragraph(f'🔍 Сэдэв: {topic}')
    doc.add_heading('📝 Төлөвлөгөө:', level=1)
    doc.add_paragraph(text)
    
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# 4. ПРОГРАММЫН ҮНДСЭН ХЭСЭГ
st.title("🎓 Ухаалаг Багшийн Туслах")
st.write("Gemini 1.5 Flash - Монгол хэл дээрх хамгийн сүүлийн хувилбар")

# Оруулах талбарууд
col1, col2 = st.columns(2)
with col1:
    subject = st.selectbox("📚 Хичээл сонгох", ["Математик", "Мэдээлэл технологи", "Монгол хэл", "Физик", "Биологи", "Хими", "Түүх"])
    grade = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)])
with col2:
    topic = st.text_input("🔍 Хичээлийн сэдэв", placeholder="Жишээ: Нарны систем")
    duration = st.slider("⏱️ Хугацаа (минут)", 20, 90, 40)

# Үр дүн гаргах
if st.button("✨ Хичээл төлөвлөгөө боловсруулах"):
    if not topic:
        st.warning("⚠️ Хичээлийн сэдвээ оруулна уу!")
    else:
        try:
            with st.spinner("🛠️ AI төлөвлөгөөг боловсруулж байна..."):
                # Илүү тодорхой заавар (Prompt)
                prompt = (f"Чи бол туршлагатай багш. {subject} хичээлийн {grade}-д орох '{topic}' сэдвээр "
                         f"{duration} минутын хичээлийн төлөвлөгөөг Монгол хэл дээр маш тодорхой, "
                         f"бүтэцтэйгээр (зорилго, явц, дүгнэлт) гаргаж өг.")
                
                response = model.generate_content(prompt)
                
                if response.text:
                    st.markdown("---")
                    st.markdown("### 📝 Боловсруулсан төлөвлөгөө")
                    st.write(response.text)
                    
                    # Word файлаар татах
                    word_file = create_word_file(response.text, subject, topic)
                    st.download_button(
                        label="💾 Word файлаар татах",
                        data=word_file,
                        file_name=f"{topic}_tolovlogo.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.error("AI хариу ирүүлсэнгүй. Дахин оролдоно уу.")
        except Exception as e:
            st.error(f"Алдаа гарлаа: {e}")
            st.info("Зөвлөмж: Шинэ API Key-ээ Secrets хэсэгт зөв оруулсан эсэхээ шалгаарай.")
