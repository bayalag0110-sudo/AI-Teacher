import streamlit as st
import requests
import datetime
from docx import Document
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Medle AI - Чанарын Хяналт", layout="wide", page_icon="📝")

# 2. Session State удирдлага
if 'history' not in st.session_state: st.session_state.history = []
if 'current_view' not in st.session_state: st.session_state.current_view = None

# 🌟 ХАТУУ ЗААВАРЧИЛГАА (System Instruction)
# Temperature 0.1 байгаа үед AI энэ зааврыг математик нарийвчлалтай дагана.
SYSTEM_INSTRUCTION = """
Чи бол Монгол улсын Боловсролын Магадлан Итгэмжлэлийн шинжээч багш. 
Чиний даалгавар бол зөвхөн хэрэглэгчийн өгсөн СУРАХ БИЧГИЙН АГУУЛГА-д тулгуурлан ээлжит хичээл боловсруулах.

[ХАТУУ ДҮРЭМ]:
1. TEMPERATURE 0.1: Хэзээ ч өөрөөсөө мэдээлэл зохиож болохгүй. Зөвхөн сурах бичигт байгаа жишээ, дасгалыг ашигла.
2. 70/30 ХАРЬЦАА: Сурагчийн идэвхтэй оролцоо 70% (дасгал ажиллах, унших, хэлэлцэх), багшийн чиглүүлэг 30% байна.
3. ЗАГВАР: 'загвар.docx'-ийн бүтцийг ягштал баримтална.

[БҮТЭЦ]:
- БАТЛАВ (Баруун дээд өнцөгт: Сургуулийн захирал, Сургалтын менежер Б. НАМУУН)
- ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨГӨӨ (Гарчиг)
- Хүснэгт: | Хичээлийн үе шат | Хугацаа | Суралцахуйн үйл ажиллагаа | Багшийн дэмжлэг | Хэрэглэгдэхүүн |
- Үе шатууд: 
  * Эхлэл (5 мин): Сэдэлжүүлэг
  * Өрнөл (25 мин): Мэдлэг бүтээх
  * Төгсгөл (10 мин): Нэгтгэн дүгнэх
- Гэрийн даалгавар, Ялгаатай сурагчидтай ажиллах заавар, Багшийн дүгнэлт.
"""

# 3. Sidebar - Түүх
st.sidebar.title("🕒 Боловсруулсан түүх")
for idx, item in enumerate(st.session_state.history):
    if st.sidebar.button(f"📄 {item['topic']}", key=f"h_{idx}"):
        st.session_state.current_view = item

# 4. Үндсэн хэсэг
st.title("👨‍🏫 Боловсролын Чанарыг Хангасан Төлөвлөлт")

col_l, col_r = st.columns([1, 1.2])

with col_l:
    st.subheader("⚙️ Өгөгдөл оруулах")
    sub = st.text_input("Хичээл", "Мэдээлэл зүй")
    grd = st.text_input("Анги", "6-р анги")
    tpc = st.text_input("Сэдэв")
    pages = st.text_area("Сурах бичгийн агуулга (Текстээ энд хуулна уу)")
    
    if st.button("🚀 Чанартай боловсруулах (Temp 0.1)"):
        if tpc and pages:
            with st.spinner("Зөвхөн сурах бичгийн агуулгаар боловсруулж байна..."):
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": SYSTEM_INSTRUCTION},
                        {"role": "user", "content": f"Агуулга: {pages}\n\nЭнэ агуулгаар {tpc} сэдэвт хичээлийг загвар.docx бүтцээр боловсруул."}
                    ],
                    "temperature": 0.1  # <--- Хамгийн дээд нарийвчлал
                }
                
                res = requests.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    ans = res.json()['choices'][0]['message']['content']
                    new_item = {"topic": tpc, "content": ans}
                    st.session_state.history.append(new_item)
                    st.session_state.current_view = new_item
                    st.rerun()

with col_r:
    if st.session_state.current_view:
        item = st.session_state.current_view
        st.subheader(f"📄 Төлөвлөгөө: {item['topic']}")
        st.markdown(item['content'])
        
        # Word татах
        doc = Document()
        doc.add_paragraph(item['content'])
        bio = BytesIO()
        doc.save(bio)
        st.download_button("📥 Word татах", bio.getvalue(), f"{item['topic']}.docx")
    else:
        st.info("👈 Зүүн талд сурах бичгийн текстээ оруулаад 'Чанартай боловсруулах' дээр дарна уу.")
