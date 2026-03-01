import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# 1. ТОГТВОРТОЙ ХОЛБОЛТЫН ТОХИРГОО
try:
    # Secrets-ээс шинэ түлхүүрийг унших
    api_key = st.secrets["GOOGLE_API_KEY"]
    
    # ХАМГИЙН ЧУХАЛ: 'rest' тээвэрлэлт ашиглаж v1beta-аас зайлсхийх
    genai.configure(api_key=api_key, transport='rest')
    
    # Хамгийн сүүлийн үеийн тогтвортой загвар (v1 хувилбар)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Тохиргооны алдаа: {e}")
    st.stop()

# 2. ВЭБ САЙТЫН ДИЗАЙН
st.set_page_config(page_title="Ухаалаг Багшийн Туслах", page_icon="🎓")
st.title("🎓 Ухаалаг Багшийн Туслах")
st.write("Орчин: Streamlit Cloud | AI: Gemini 1.5 Flash")

# 3. ОРУУЛАХ ХЭСЭГ
subject = st.selectbox("📚 Хичээл сонгох", ["Математик", "Мэдээлэл технологи", "Монгол хэл", "Физик", "Биологи"])
grade = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)])
topic = st.text_input("🔍 Хичээлийн сэдэв", placeholder="Жишээ: Нарны систем")
duration = st.slider("⏱️ Хугацаа (минут)", 20, 90, 40)

# 4. ТӨЛӨВЛӨГӨӨ БОЛОВСРУУЛАХ
if st.button("✨ Хичээл төлөвлөгөө боловсруулах"):
    if not topic:
        st.warning("⚠️ Сэдвээ оруулна уу!")
    else:
        try:
            with st.spinner("🛠️ AI ажиллаж байна..."):
                # Төлөвлөгөө гаргах заавар
                prompt = (f"{subject} хичээлийн {grade}-д орох '{topic}' сэдвээр "
                         f"{duration} минутын хичээлийн төлөвлөгөөг Монгол хэл дээр "
                         f"маш тодорхой, бүтцийн дагуу гаргаж өг.")
                
                response = model.generate_content(prompt)
                
                if response.text:
                    st.markdown("---")
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
            st.error(f"Алдаа гарлаа: {e}")
