import streamlit as st
import requests
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import datetime

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Ухаалаг Багшийн Туслах", page_icon="🎓", layout="wide")

st.title("🎓 Ээлжит хичээлийн төлөвлөлт")
st.info("Таны ирүүлсэн албан ёсны загварын дагуу AI төлөвлөгөө боловсруулна.")

# 2. Secrets-ээс Groq API Key-ийг унших
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("Secrets хэсэгт GROQ_API_KEY-ээ оруулна уу.")
    st.stop()

# 3. AI холболтын функц (Llama 3.3)
def generate_lesson_plan(subject, grade, topic, duration, date):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Загвар файл дахь бүтцийг AI-д зааварчилж байна
    prompt = f"""
Чи бол Монгол улсын боловсролын салбарын мэргэжилтэн багш. 
Дараах мэдээллийн дагуу "ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ"-ийг боловсруулж өг.
Мэдээлэл: Хичээл: {subject}, Анги: {grade}, Сэдэв: {topic}, Хугацаа: {duration} минут, Огноо: {date}.

Хариултыг заавал дараах бүтцээр (хүснэгт болон текст) гарга:
1. Хичээлийн зорилго: (Сурагч юу сурч мэдэх вэ?)
2. Үйл явц (Хичээлийн үе шат бүрээр):
   - Эхлэл хэсэг (хичээлийн зорилго тодорхой болгох, сэдэлжүүлэг, сэргээн санах): Хугацаа, Суралцахуйн үйл ажиллагаа, Багшийн дэмжлэг, Хэрэглэгдэхүүн.
   - Өрнөл хэсэг (арга, мэдээлэл боловсруулах, задлан шинжлэх, мэдлэг бүтээх): Хугацаа, Суралцахуйн үйл ажиллагаа, Багшийн дэмжлэг, Хэрэглэгдэхүүн.
   - Төгсгөл хэсэг (ойлголтоо нэгтгэн дүгнэх, үнэлгээ): Хугацаа, Суралцахуйн үйл ажиллагаа, Багшийн дэмжлэг, Хэрэглэгдэхүүн.
3. Гэрийн даалгавар: (Тодорхой дасгал ажил)
4. Ялгаатай сурагчидтай ажиллах аргачлал: (Дэмжлэг шаардлагатай сурагчдад зориулсан)
5. Нэмэлт: (Багшийн дүгнэлт, анхаарах зүйлс)
"""
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Чи бол хичээлийн төлөвлөгөө боловсруулдаг мэргэжилтэн."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=40)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"❌ Алдаа: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Холболтын алдаа: {str(e)}"

# 4. Word файл үүсгэх функц (Загварын дагуу)
def create_docx(subject, grade, topic, duration, date, content):
    doc = Document()
    
    # БАТЛАВ хэсэг
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run("БАТЛАВ\nСУРГАЛТЫН МЕНЕЖЕР: .................")
    run.bold = True
    
    # Гарчиг
    title = doc.add_heading('ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Үндсэн мэдээлэл
    doc.add_paragraph(f"Анги: {grade}")
    doc.add_paragraph(f"Сар, өдөр, хугацаа: {date}, {duration} минут")
    doc.add_paragraph(f"Ээлжит хичээлийн сэдэв: {topic}")
    
    # AI-аас ирсэн контент
    doc.add_paragraph("\n" + content)
    
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# 5. Хэрэглэгчийн интерфейс
with st.sidebar:
    st.header("⚙️ Тохиргоо")
    subject = st.text_input("📚 Хичээлийн нэр", "Мэдээлэл зүй")
    grade = st.selectbox("🏫 Анги", [f"{i}-р анги" for i in range(1, 13)], index=6)
    date = st.date_input("📅 Огноо", datetime.date.today())
    duration = st.number_input("⏱️ Хугацаа (минут)", value=40)

topic = st.text_input("🔍 Ээлжит хичээлийн сэдэв оруулна уу", placeholder="Жишээ: Энгийн бутархай")

if st.button("✨ Төлөвлөгөө боловсруулах"):
    if not topic:
        st.warning("⚠️ Хичээлийн сэдвээ оруулна уу.")
    else:
        with st.spinner("Таны ирүүлсэн загварын дагуу AI ажиллаж байна..."):
            result = generate_lesson_plan(subject, grade, topic, duration, date)
            st.divider()
            st.markdown(result)
            
            # Word татах хэсэг
            docx_file = create_docx(subject, grade, topic, duration, date, result)
            st.download_button(
                label="📥 Төлөвлөгөөг Word файлаар татах",
                data=docx_file,
                file_name=f"Eeljit_Plan_{topic}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
