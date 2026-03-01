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

# 🌟 ХАТУУ ЗААВАРЧИЛГАА (System Instruction)
SYSTEM_INSTRUCTION = """
Чи бол Монгол улсын Боловсролын шинжээч багш. 
Чиний даалгавар бол зөвхөн хэрэглэгчийн оруулсан PDF ФАЙЛЫН ТЕКСТ-д тулгуурлан 'ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ.docx' бүтцээр төлөвлөгөө гаргах.

[МӨРДӨХ ХАТУУ ДҮРЭМ]:
1. TEMPERATURE 0.1: Зөвхөн сурах бичигт байгаа дасгал, даалгавар, мэдээллийг ашигла. Юу ч зохиож болохгүй.
2. 70/30 ХАРЬЦАА: Сурагчийн идэвхтэй оролцоо 70% (унших, дасгал ажиллах), багшийн дэмжлэг 30% байна.
3. ЗАГВАРЫН БҮТЭЦ:
   - БАТЛАВ (Баруун дээд талд) СУРГАЛТЫН МЕНЕЖЕР Б. НАМУУН
   - ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ (Гарчиг)
   - Анги, Сар өдөр, Сэдэв, Зорилго (Сурах бичгээс)
   - Үйл явц (Хүснэгтээр: Эхлэл 5', Өрнөл 25', Төгсгөл 10')
   - Гэрийн даалгавар, Ялгаатай сурагчдын аргачлал, Багшийн дүгнэлт.
"""

# PDF-ээс текст унших функц
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# 3. Sidebar - Түүх
st.sidebar.title("🕒 Боловсруулсан түүх")
for idx, item in enumerate(st.session_state.history):
    if st.sidebar.button(f"📄 {item['topic']}", key=f"h_{idx}"):
        st.session_state.current_view = item

# 4. Үндсэн цонх
st.title("👨‍🏫 PDF Сурах бичгээс хичээл төлөвлөх")

col_in, col_out = st.columns([1, 1.2])

with col_in:
    st.subheader("📁 Сурах бичиг оруулах")
    uploaded_pdf = st.file_uploader("Сурах бичгийн PDF файлаа энд оруулна уу", type="pdf")
    
    sub = st.text_input("Хичээл", "Мэдээлэл зүй")
    grd = st.text_input("Анги", "6а")
    tpc = st.text_input("Хичээлийн сэдэв (PDF-ээс хайх сэдэв)")
    
    if st.button("🚀 PDF-ээс боловсруулах"):
        if uploaded_pdf and tpc:
            with st.spinner("PDF файлыг уншиж, төлөвлөгөө гаргаж байна..."):
                # 1. Текст ялгаж авах
                pdf_text = extract_text_from_pdf(uploaded_pdf)
                
                # 2. AI руу хүсэлт илгээх
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": SYSTEM_INSTRUCTION},
                        {"role": "user", "content": f"PDF Агуулга: {pdf_text[:10000]}\n\nСэдэв: {tpc}\nАнги: {grd}\nХичээл: {sub}"}
                    ],
                    "temperature": 0.1
                }
                
                res = requests.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    ans = res.json()['choices'][0]['message']['content']
                    new_item = {"topic": tpc, "content": ans, "date": datetime.datetime.now().strftime("%H:%M")}
                    st.session_state.history.append(new_item)
                    st.session_state.current_view = new_item
                    st.rerun()
        else:
            st.warning("⚠️ PDF файл болон сэдвээ оруулна уу.")

with col_out:
    if st.session_state.current_view:
        item = st.session_state.current_view
        st.subheader(f"📄 {item['topic']}")
        st.markdown(item['content'])
        
        # Word татах
        doc = Document()
        doc.add_paragraph(item['content'])
        bio = BytesIO()
        doc.save(bio)
        st.download_button("📥 Word татах", bio.getvalue(), f"{item['topic']}.docx")
    else:
        st.info("👈 PDF файлаа оруулж, сэдвээ бичээд 'Боловсруулах' дээр дарна уу.")
