import streamlit as st
import requests
import datetime
from docx import Document
from io import BytesIO
import PyPDF2  # PDF-ээс текст унших сан

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Medle AI - PDF Төлөвлөгч", layout="wide", page_icon="📚")

# 2. Session State удирдлага
if 'history' not in st.session_state: st.session_state.history = []
if 'current_view' not in st.session_state: st.session_state.current_view = None

# 🌟 ХАТУУ ЗААВАРЧИЛГАА (System Instruction) - ТАНЫ ЗАГВАР ДАГУУ
SYSTEM_INSTRUCTION = """
Чи бол Монгол улсын Боловсролын шинжээч багш. 
Чиний даалгавар бол зөвхөн хэрэглэгчийн оруулсан PDF ФАЙЛЫН ТЕКСТ-д тулгуурлан 'ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ.docx' бүтцээр төлөвлөгөө гаргах.

[МӨРДӨХ ХАТУУ ДҮРЭМ]:
1. TEMPERATURE 0.1: Зөвхөн сурах бичигт байгаа дасгал, даалгавар, мэдээллийг ашигла. Юу ч зохиож болохгүй.
2. 70/30 ХАРЬЦАА: Сурагчийн идэвхтэй оролцоо 70%, багшийн дэмжлэг 30% байна.
3. ЗАГВАРЫН БҮТЭЦ:
   - БАТЛАВ (Баруун дээд талд) СУРГАЛТЫН МЕНЕЖЕР Б. НАМУУН
   - ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ (Гарчиг)
   - Анги, Сар өдөр, Сэдэв, Зорилго (Зөвхөн PDF-ээс)
   - Үйл явц (Хүснэгтээр: Эхлэл 5 минут, Өрнөл 25 минут, Төгсгөл 10 минут)
   - Гэрийн даалгавар, Ялгаатай сурагчидтай ажиллах аргачлал, Багшийн дүгнэлт.
"""

# PDF-ээс текст унших функц
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        t = page.extract_text()
        if t: text += t
    return text

# 3. Sidebar - Түүх хадгалах
st.sidebar.title("🕒 Боловсруулсан түүх")
if st.sidebar.button("➕ Шинэ төлөвлөгөө"):
    st.session_state.current_view = None
    st.rerun()

st.sidebar.markdown("---")
for idx, item in enumerate(st.session_state.history):
    if st.sidebar.button(f"📄 {item['topic']}", key=f"h_{idx}"):
        st.session_state.current_view = item

# 4. Үндсэн цонх
st.title("👨‍🏫 PDF Сурах бичгээс ээлжит хичээл төлөвлөх")

col_in, col_out = st.columns([1, 1.2])

with col_in:
    st.subheader("📁 PDF файл оруулах")
    uploaded_pdf = st.file_uploader("Сурах бичгийн PDF файлаа (хуудсаа) оруулна уу", type="pdf")
    
    sub = st.text_input("Хичээл", "Мэдээлэл зүй")
    grd = st.text_input("Анги", "6а")
    tpc = st.text_input("Хичээлийн сэдэв (PDF-ээс хайх)")
    
    if st.button("🚀 PDF-ээс боловсруулах"):
        if uploaded_pdf and tpc:
            with st.spinner("PDF-ээс агуулгыг шүүж, чанартай төлөвлөгөө гаргаж байна..."):
                # 1. Текст ялгах
                full_text = extract_text_from_pdf(uploaded_pdf)
                
                # 2. API хүсэлт
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                
                # PDF текст хэт том бол эхний 8000 тэмдэгтийг авах (Context limit)
                context_text = full_text[:8000] 
                
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": SYSTEM_INSTRUCTION},
                        {"role": "user", "content": f"Сурах бичгийн PDF текст: {context_text}\n\nСэдэв: {tpc}\nАнги: {grd}\nХичээл: {sub}"}
                    ],
                    "temperature": 0.1
                }
                
                res = requests.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    ans = res.json()['choices'][0]['message']['content']
                    new_item = {
                        "topic": tpc, 
                        "content": ans, 
                        "date": datetime.datetime.now().strftime("%H:%M")
                    }
                    st.session_state.history.append(new_item)
                    st.session_state.current_view = new_item
                    st.rerun()
        else:
            st.warning("⚠️ PDF файл болон сэдвийн нэрээ оруулна уу.")

with col_out:
    if st.session_state.current_view:
        item = st.session_state.current_view
        st.subheader(f"📄 {item['topic']}")
        st.markdown(item['content'])
        
        # Word файл болгож татах
        doc = Document()
        doc.add_paragraph(item['content'])
        bio = BytesIO()
        doc.save(bio)
        st.download_button("📥 Word татах", bio.getvalue(), f"{item['topic']}.docx")
    else:
        st.info("👈 PDF сурах бичгээ оруулж, сэдвээ бичээд 'Боловсруулах' товчийг дарна уу.")
