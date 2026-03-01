import streamlit as st
import requests
import json
from docx import Document
from io import BytesIO

# 1. Тохиргоо
st.set_page_config(page_title="Ухаалаг Багшийн Туслах", page_icon="🎓")

if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Secrets хэсэгт GOOGLE_API_KEY-ээ оруулна уу.")
    st.stop()

# 2. AI холболтын функц
def generate_lesson_plan(subject, grade, topic, duration):
    # Хамгийн тогтвортой 'gemini-pro' загварыг ашиглах
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    prompt = f"{subject} хичээлийн {grade}-д орох '{topic}' сэдвээр {duration} минутын хичээлийн төлөвлөгөөг Монгол хэл дээр маш тодорхой гаргаж өг."
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        # Хэрэв gemini-pro ажиллахгүй бол өөр хувилбарыг турших
        alt_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={api_key}"
        alt_response = requests.post(alt_url, headers=headers, data=json.dumps(data))
        if alt_response.status_code == 200:
            return alt_response.json()['candidates'][0]['content']['parts'][0]['text']
        
        raise Exception(f"Код: {response.status_code}, Тайлагнал: {response.text}")

# 3. Вэб дизайн
st.title("🎓 Ухаалаг Багшийн Туслах")
st.info("Тогтвортой 'Gemini Pro' загварыг ашиглаж байна.")

subject = st.selectbox("📚 Хичээл", ["Математик", "Мэдээлэл технологи", "Монгол хэл", "Физик", "Биологи"])
grade = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)])
topic = st.text_input("🔍 Хичээлийн сэдэв")
duration = st.slider("⏱️ Хугацаа (мин)", 20, 90, 40)

if st.button("✨ Хичээл төлөвлөгөө боловсруулах"):
    if not topic:
        st.warning("⚠️ Сэдвээ оруулна уу!")
    else:
        try:
            with st.spinner("🛠️ AI ажиллаж байна..."):
                plan_text = generate_lesson_plan(subject, grade, topic, duration)
                st.markdown("### 📝 Боловсруулсан төлөвлөгөө")
                st.write(plan_text)
                
                # Word файл
                doc = Document()
                doc.add_heading('ХИЧЭЭЛИЙН ТӨЛӨВЛӨГӨӨ', 0)
                doc.add_paragraph(plan_text)
                bio = BytesIO()
                doc.save(bio)
                bio.seek(0)
                
                st.download_button(label="💾 Word файл татах", data=bio, file_name=f"{topic}.docx")
        except Exception as e:
            st.error(f"Алдаа: {e}")
