import streamlit as st
import requests
import json
from docx import Document
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Ухаалаг Багшийн Туслах", page_icon="🎓")

st.title("🎓 Ухаалаг Багшийн Туслах")
st.success("Llama 3.3 шинэ загвар идэвхжлээ.")

# 2. Secrets-ээс Groq API Key-ийг унших
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("Secrets хэсэгт GROQ_API_KEY-ээ оруулна уу.")
    st.stop()

# 3. AI холболтын функц (Groq - Шинэчилсэн загвар)
def generate_lesson_plan(subject, grade, topic, duration):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"Чи бол туршлагатай багш. {subject} хичээлийн {grade}-д орох '{topic}' сэдвээр {duration} минутын хичээлийн төлөвлөгөөг Монгол хэл дээр маш цэгцтэй гаргаж өг."
    
    payload = {
        "model": "llama-3.3-70b-versatile", # ЭНЭ ХЭСГИЙГ ШИНЭЧИЛЛЭЭ
        "messages": [
            {"role": "system", "content": "Чи хичээлийн төлөвлөгөө гаргадаг мэргэжилтэн."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"❌ Алдаа: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Холболтын алдаа: {str(e)}"

# 4. Word файл болгон хөрвүүлэх функц
def create_docx(text):
    doc = Document()
    doc.add_heading('Хичээлийн төлөвлөгөө', 0)
    doc.add_paragraph(text)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# 5. Хэрэглэгчийн интерфейс
subject = st.selectbox("📚 Хичээл", ["Математик", "Монгол хэл", "Биологи", "Физик", "Хими", "Мэдээлэл зүй"])
grade = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)])
topic = st.text_input("🔍 Хичээлийн сэдэв", placeholder="Жишээ: Энгийн бутархай")
duration = st.slider("⏱️ Хугацаа (минут)", 20, 90, 40)

if st.button("✨ Хичээл төлөвлөгөө боловсруулах"):
    if not topic:
        st.warning("⚠️ Сэдвээ оруулна уу.")
    else:
        with st.spinner("AI төлөвлөгөө боловсруулж байна..."):
            result = generate_lesson_plan(subject, grade, topic, duration)
            st.divider()
            st.markdown(result)
            
            # Татаж авах хэсэг
            docx_file = create_docx(result)
            st.download_button(
                label="📥 Төлөвлөгөөг Word хэлбэрээр татах",
                data=docx_file,
                file_name=f"plan_{topic}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
