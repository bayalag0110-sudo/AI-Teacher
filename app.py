import streamlit as st
import requests
import json
from docx import Document
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Ухаалаг Багшийн Туслах", page_icon="🎓")

st.title("🎓 Ээлжит хичээлийн төлөвлөлт")
st.info("Таны ирүүлсэн албан ёсны загварын дагуу AI төлөвлөгөө боловсруулна.")

# 2. Secrets-ээс Groq API Key-ийг унших
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("Secrets хэсэгт GROQ_API_KEY-ээ оруулна уу.")
    st.stop()

# 3. AI холболтын функц (Llama 3.3)
def generate_lesson_plan(subject, grade, topic, duration):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Загварын дагуу өгөх заавар (Prompt)
    prompt = f"""
Чи бол Монгол улсын боловсролын салбарын мэргэжилтэн багш. 
Дараах мэдээллийн дагуу "ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ"-ийг боловсруулж өг.
Мэдээлэл: Хичээл: {subject}, Анги: {grade}, Сэдэв: {topic}, Хугацаа: {duration} минут.

Хариултыг заавал дараах бүтцээр гарга:
1. Хичээлийн зорилго: (Тодорхой бичих)
2. Үйл явц (Хүснэгт хэлбэрээр):
   - Эхлэл хэсэг (хичээлийн зорилго тодорхой болгох, сэдэлжүүлэг, сэргээн санах)
   - Өрнөл хэсэг (арга, мэдээлэл боловсруулах, задлан шинжлэх, мэдлэг бүтээх)
   - Төгсгөл хэсэг (ойлголтоо нэгтгэн дүгнэх, үнэлгээ)
3. Гэрийн даалгавар
4. Ялгаатай сурагчидтай ажиллах аргачлал
5. Нэмэлт (багшийн анхаарах зүйлс)
"""
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Чи бол ээлжит хичээлийн төлөвлөлт гаргадаг туслах."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"❌ Алдаа: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Холболтын алдаа: {str(e)}"

# 4. Word файл үүсгэх функц
def create_docx(text):
    doc = Document()
    doc.add_heading('ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ', 0)
    doc.add_paragraph(text)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# 5. Хэрэглэгчийн интерфейс
col1, col2 = st.columns(2)
with col1:
    subject = st.text_input("📚 Хичээлийн нэр", "Математик")
    grade = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)])
with col2:
    topic = st.text_input("🔍 Ээлжит хичээлийн сэдэв")
    duration = st.number_input("⏱️ Хугацаа (минут)", value=40)

if st.button("✨ Төлөвлөгөө боловсруулах"):
    if not topic:
        st.warning("⚠️ Сэдвээ оруулна уу.")
    else:
        with st.spinner("Таны ирүүлсэн загварын дагуу боловсруулж байна..."):
            result = generate_lesson_plan(subject, grade, topic, duration)
            st.divider()
            st.markdown(result)
            
            docx_file = create_docx(result)
            st.download_button(
                label="📥 Төлөвлөгөөг Word файлаар татах",
                data=docx_file,
                file_name=f"plan_{topic}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
