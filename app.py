import streamlit as st
import requests
import datetime
from docx import Document
from io import BytesIO
import PyPDF2

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="EduPlan AI - Заах Аргач", layout="wide", page_icon="🎓")

# CSS - Портал сайтуудын харагдацыг сайжруулах
st.markdown("""
    <style>
    .portal-link { padding: 10px; border-radius: 5px; background-color: #f0f2f6; border-left: 5px solid #28a745; margin-bottom: 5px; display: block; text-decoration: none; color: #31333F; font-weight: bold; }
    .portal-link:hover { background-color: #e0e4ea; }
    iframe { border: 1px solid #ddd; border-radius: 10px; width: 100%; height: 600px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Session State - Түүх хадгалах
if 'history' not in st.session_state: st.session_state.history = []
if 'current_view' not in st.session_state: st.session_state.current_view = None

# 🌟 ХАТУУ ЗААВАРЧИЛГАА (System Instruction)
SYSTEM_INSTRUCTION = """
Чи бол Монгол улсын Боловсролын шинжээч багш. 
Чиний даалгавар бол зөвхөн хэрэглэгчийн оруулсан PDF ФАЙЛ-д тулгуурлан 'ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ.docx' бүтцээр төлөвлөгөө гаргах.

[МӨРДӨХ ХАТУУ ДҮРЭМ]:
1. TEMPERATURE 0.1: Зөвхөн сурах бичигт байгаа дасгал, даалгавар, мэдээллийг ашигла. Юу ч зохиож болохгүй.
2. 70/30 ХАРЬЦАА: Сурагчийн идэвхтэй оролцоо 70% (унших, дасгал ажиллах), багшийн дэмжлэг 30% байна.
3. ЗАГВАРЫН БҮТЭЦ (ЯГШТАЛ БАРИМТАЛ):
   БАТЛАВ                                             СУРГАЛТЫН МЕНЕЖЕР                              Б. НАМУУН
   ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨГӨӨ
   Анги:  
   Сар, өдөр, хугацаа: 
   Ээлжит хичээлийн сэдэв:  
   Хичээлийн зорилго:  
   Үйл явц:
   | Хичээлийн үе шат | Хугацаа | Суралцахуйн үйл ажиллагаа | Багшийн дэмжлэг | Хэрэглэгдэхүүн |
   | :--- | :--- | :--- | :--- | :--- |
   | Эхлэл хэсэг /сэдэлжүүлэг/ | 5 минут | | | |
   | Өрнөл хэсэг /мэдлэг бүтээх/ | 25 минут | | | |
   | Төгсгөл хэсэг /дүгнэлт/ | 10 минут | | | |
   
   Гэрийн даалгавар:
   Ялгаатай сурагчидтай ажиллах аргачлал:
   Нэмэлт: тухайн хичээлийн талаарх багшийн дүгнэлт:
"""

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        t = page.extract_text()
        if t: text += t
    return text

# 3. Sidebar - Түүх болон Портал сайтууд
with st.sidebar:
    st.title("🎓 Багшийн туслах")
    
    st.subheader("🌐 Сургалтын порталууд")
    portals = {
        "Econtent (Сурах бичиг)": "https://econtent.edu.mn/book",
        "Medle.mn (Цахим сургалт)": "https://medle.mn/",
        "EduMap (Хичээл төлөвлөлт)": "https://edumap.mn/",
        "ESIS (Багшийн бүртгэл)": "https://bagsh.esis.edu.mn/",
        "Bagsh.edu.mn (Портал)": "https://bagsh.edu.mn/"
    }
    for name, url in portals.items():
        st.markdown(f'<a href="{url}" target="_blank" class="portal-link">{name}</a>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("🕒 Төлөвлөгөөний түүх")
    if st.button("➕ Шинэ төлөвлөгөө"):
        st.session_state.current_view = None
        st.rerun()
    
    for idx, item in enumerate(st.session_state.history):
        if st.sidebar.button(f"📄 {item['topic']} ({item['time']})", key=f"h_{idx}"):
            st.session_state.current_view = item

# 4. Үндсэн цонх
st.title("👨‍🏫 Ээлжит хичээл боловсруулах систем")

col_in, col_out = st.columns([1, 1.2])

with col_in:
    st.subheader("⚙️ Оролтын өгөгдөл")
    uploaded_file = st.file_uploader("Сурах бичгийн PDF оруулна уу", type="pdf")
    sub = st.text_input("Хичээл", "Мэдээлэл зүй")
    grd = st.text_input("Анги", "6а")
    tpc = st.text_input("Хичээлийн сэдэв")
    
    if st.button("🚀 Боловсруулах (Temp 0.1)"):
        if uploaded_file and tpc:
            with st.spinner("PDF-ээс агуулгыг шүүж, загварын дагуу бэлтгэж байна..."):
                pdf_text = extract_text_from_pdf(uploaded_file)
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": SYSTEM_INSTRUCTION},
                        {"role": "user", "content": f"PDF Текст: {pdf_text[:8000]}\n\nСэдэв: {tpc}\nАнги: {grd}\nХичээл: {sub}"}
                    ],
                    "temperature": 0.1
                }
                
                res = requests.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    ans = res.json()['choices'][0]['message']['content']
                    new_item = {
                        "topic": tpc, "content": ans, 
                        "time": datetime.datetime.now().strftime("%m/%d %H:%M"),
                        "sub": sub, "grd": grd
                    }
                    st.session_state.history.append(new_item)
                    st.session_state.current_view = new_item
                    st.rerun()

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
        st.info("👈 Зүүн талаас PDF-ээ оруулж, сэдвээ бичнэ үү.")

# 5. Порталыг шууд доор нь харах (Сонгосон бол)
st.divider()
st.subheader("🌐 Сургалтын портал харах")
portal_choice = st.selectbox("Портал сонгох:", list(portals.values()))
st.components.v1.iframe(portal_choice, height=700, scrolling=True)
