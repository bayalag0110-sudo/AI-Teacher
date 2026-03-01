import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# 1. Тогтвортой AI тохиргоо
try:
    # Secrets-ээс түлхүүрийг найдвартай унших
    api_key = st.secrets["GOOGLE_API_KEY"]
    
    # v1 тогтвортой хувилбарыг REST-ээр холбох (404 алдаанаас сэргийлнэ)
    genai.configure(api_key=api_key, transport='rest')
    
    # Хамгийн сүүлийн үеийн тогтвортой загвар
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Тохиргооны алдаа гарлаа. Secrets-ээ шалгана уу.")
    st.stop()

# 2. Вэб хуудасны дизайн
st.set_page_config(page_title="Ухаалаг Багшийн Туслах", page_icon="🎓")
st.title("🎓 Ухаалаг Багшийн Туслах")
st.write("Орчин: Streamlit Cloud | AI: Gemini 1.5 Flash")

# 3. Мэдээлэл оруулах
subject = st.selectbox("📚 Хичээл", ["Математик", "Мэдээлэл технологи", "Монгол хэл", "Физик", "Биологи"])
grade = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)])
topic = st.text_input("🔍 Хичээлийн сэдэв", placeholder="Жишээ: Нарны систем")
duration = st.slider("⏱️ Хугацаа (мин)", 20, 90, 40)

# 4. Төлөвлөгөө боловсруулах
if st.button("✨ Хичээл төлөвлөгөө боловсруулах"):
    if not topic:
        st.warning("⚠️ Сэдвээ оруулна уу!")
    else:
        try:
            with st.spinner("🛠️ AI ажиллаж байна..."):
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
            st.error(f"Алдаа: {e}")
