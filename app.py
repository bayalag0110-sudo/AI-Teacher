import streamlit as st
import requests
import json
from docx import Document
from io import BytesIO

# 1. Төхөөрөмжийн тохиргоо
st.set_page_config(page_title="Ухаалаг Багшийн Туслах", page_icon="🎓")

# Secrets-ээс шинэ API Key-ийг унших
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Secrets хэсэгт GOOGLE_API_KEY-ээ оруулна уу.")
    st.stop()

# 2. AI холболт - ТОГТВОРТОЙ V1 ХУВИЛБАР
def generate_lesson_plan(subject, grade, topic, duration):
    # Хамгийн тогтвортой V1 хаяг руу шилжүүлэв (404 алдаанаас сэргийлнэ)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    prompt = f"Чи бол туршлагатай багш. {subject} хичээлийн {grade}-д орох '{topic}' сэдвээр {duration} минутын хичээлийн төлөвлөгөөг Монгол хэл дээр маш тодорхой гаргаж өг."
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    # API хүсэлт илгээх
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        # Алдаа гарвал дэлгэрэнгүй харуулна
        raise Exception(f"Алдааны код: {response.status_code}, Тайлагнал: {response.text}")

# 3. Вэб дизайн
st.title("🎓 Ухаалаг Багшийн Туслах")
st.info("Хамгийн тогтвортой Gemini v1 холболт идэвхжлээ.")

subject = st.selectbox("📚 Хичээл", ["Математик", "Мэдээлэл технологи", "Монгол хэл", "Физик", "Биологи", "Хими", "Түүх"])
grade = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)])
topic = st.text_input("🔍 Хичээлийн сэдэв", placeholder="Жишээ: Нарны систем")
duration = st.slider("⏱️ Хугацаа (минут)", 20, 90, 40)

if st.button("✨ Хичээл төлөвлөгөө боловсруулах"):
    if not topic:
        st.warning("⚠️ Сэдвээ оруулна уу!")
    else:
        try:
            with st.spinner("🛠️ AI ажиллаж байна..."):
                plan_text = generate_lesson_plan(subject, grade, topic, duration)
                st.markdown("---")
                st.markdown("### 📝 Боловсруулсан төлөвлөгөө")
                st.write(plan_text)
                
                # Word файл үүсгэх
                doc = Document()
                doc.add_heading('ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨГӨӨ', 0)
                doc.add_paragraph(plan_text)
                bio = BytesIO()
                doc.save(bio)
                bio.seek(0)
                
                st.download_button(label="💾 Word файл татах", data=bio, file_name=f"{topic}.docx")
        except Exception as e:
            st.error(f"Алдаа: {e}")
