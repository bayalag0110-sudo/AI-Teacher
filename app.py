import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# 1. API Түлхүүр тохиргоо
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Найдвартай модель сонгох логик
    # Хэрэв flash ажиллахгүй бол pro хувилбарыг туршина
    model_name = 'gemini-1.5-pro' # Илүү тогтвортой хувилбар руу шилжүүлэв
    model = genai.GenerativeModel(model_name)
except Exception as e:
    st.error("Secrets тохиргоог шалгана уу.")
    st.stop()

# 2. Вэб хуудасны дизайн
st.set_page_config(page_title="Ухаалаг Багшийн Туслах", page_icon="🎓")

# 3. Програмын үндсэн хэсэг
st.title("🎓 Ухаалаг Багшийн Туслах")
st.write(f"Орчин: Streamlit Cloud | AI: {model_name}")

subject = st.selectbox("📚 Хичээл", ["Математик", "Мэдээлэл технологи", "Монгол хэл", "Физик", "Биологи"])
grade = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)])
topic = st.text_input("🔍 Хичээлийн сэдэв")
duration = st.slider("⏱️ Хугацаа (мин)", 20, 90, 40)

if st.button("✨ Хичээл төлөвлөгөө боловсруулах"):
    if not topic:
        st.warning("⚠️ Хичээлийн сэдвээ оруулна уу!")
    else:
        try:
            with st.spinner("🛠️ AI төлөвлөгөө боловсруулж байна..."):
                # prompt-ийг илүү тодорхой болгох
                prompt = f"{subject} хичээлийн {grade}-д орох '{topic}' сэдвээр {duration} минутын хичээлийн төлөвлөгөөг Монгол хэл дээр гаргаж өг."
                response = model.generate_content(prompt)
                
                # Хариу ирсэн эсэхийг шалгах
                if response.text:
                    st.markdown("### 📝 Боловсруулсан төлөвлөгөө")
                    st.write(response.text)
                else:
                    st.error("AI хариу ирүүлсэнгүй. Дахин оролдоно уу.")
        except Exception as e:
            # 404 алдаа гарвал энд баригдаж, илүү ойлгомжтой тайлбар өгнө
            st.error(f"Модельтой холбогдоход алдаа гарлаа. Таны API Key 'gemini-1.5-pro' моделийг дэмжихгүй байж магадгүй. Алдааны код: {e}")
