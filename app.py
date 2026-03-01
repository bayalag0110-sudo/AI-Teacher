import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# 1. API Түлхүүр тохиргоо - v1 тогтвортой хувилбарыг ашиглах
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    # v1 хувилбар руу хүчээр шилжүүлж, REST ашиглах
    genai.configure(api_key=api_key, transport='rest')
    
    # Моделийн нэрийг хамгийн сүүлийн үеийн тогтвортой хувилбараар солих
    # 'gemini-1.5-flash-latest' эсвэл ердөө 'gemini-1.5-flash'
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"Тохиргооны алдаа: {e}")
    st.stop()

# 2. Вэб хуудасны дизайн
st.set_page_config(page_title="Ухаалаг Багшийн Туслах", page_icon="🎓")
st.title("🎓 Ухаалаг Багшийн Туслах")
st.write("Хамгийн сүүлийн үеийн Gemini 1.5 Flash загвар ашиглаж байна")

# 3. Оруулах хэсэг
subject = st.selectbox("📚 Хичээл", ["Математик", "Мэдээлэл технологи", "Монгол хэл", "Физик", "Биологи"])
grade = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)])
topic = st.text_input("🔍 Хичээлийн сэдэв")
duration = st.slider("⏱️ Хугацаа (мин)", 20, 90, 40)

# 4. Процесс
if st.button("✨ Хичээл төлөвлөгөө боловсруулах"):
    if not topic:
        st.warning("⚠️ Хичээлийн сэдвээ оруулна уу!")
    else:
        try:
            with st.spinner("🛠️ AI төлөвлөгөө боловсруулж байна..."):
                prompt = f"{subject} хичээлийн {grade}-д орох '{topic}' сэдвээр {duration} минутын хичээлийн төлөвлөгөөг Монгол хэл дээр гаргаж өг."
                response = model.generate_content(prompt)
                
                if response.text:
                    st.markdown("### 📝 Боловсруулсан төлөвлөгөө")
                    st.write(response.text)
                    
                    # Word файл үүсгэх
                    doc = Document()
                    doc.add_heading('ХИЧЭЭЛИЙН ТӨЛӨВЛӨГӨӨ', 0)
                    doc.add_paragraph(response.text)
                    bio = BytesIO()
                    doc.save(bio)
                    bio.seek(0)
                    
                    st.download_button(
                        label="💾 Word файлаар татах",
                        data=bio,
                        file_name=f"{topic}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
        except Exception as e:
            st.error(f"AI-тай холбогдоход алдаа гарлаа: {e}")
            st.info("Таны API Key Монгол улсаас хандахад хязгаарлагдсан байж магадгүй.")
