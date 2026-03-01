import streamlit as st
import requests
import datetime
from docx import Document
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Medle AI - Багшийн туслах", layout="wide", page_icon="🎓")

# CSS - Илүү цэгцтэй харагдац
st.markdown("""
    <style>
    iframe { border-radius: 12px; border: 1px solid #e0e0e0; width: 100%; height: 750px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #28a745; color: white; }
    .stExpander { border: 1px solid #f0f2f6; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Session State удирдлага
if 'history' not in st.session_state: st.session_state.history = []
if 'current_view' not in st.session_state: st.session_state.current_view = None

# 🌟 ОНОВЧТОЙ ЗААВАРЧИЛГАА (System Instruction)
SYSTEM_INSTRUCTION = """
Чи бол Монгол улсын боловсролын салбарын "Шилдэг заах аргач" багш. 
Чиний зорилго бол хэрэглэгчийн өгсөн сэдэв болон сурах бичгийн агуулгын дагуу МЭРГЭЖЛИЙН ээлжит хичээл боловсруулах.

[МӨРДӨХ ЗАРЧИМ]:
1. ИДЭВХТЭЙ СУРАЛЦАХУЙ (Active Learning): Хичээлийн үе шат бүрт сурагчийн оролцоо 70%, багшийн чиглүүлэг 30% байна.
2. БЛҮҮМИЙН ТАКСОНОМИ: Хичээлийн зорилгыг Мэдэх, Чадах, Хэрэглэх түвшинд тодорхойлно.
3. 3 ТҮВШНИЙ ДААЛГАВАР: Сорил даалгаврыг Хялбар (Сэргээн санах), Дунд (Хэрэглэх), Хүнд (Задлан шинжлэх/Бүтээх) түвшинд ялгана.

[БҮТЭЦ - 'загвар ээлжит.xlsx' ДАГУУ]:
- БАТЛАВ: Сургуулийн захирал, Сургуулийн менежер хэсэг.
- ҮЙЛ ЯВЦЫН ХҮСНЭГТ: (Үе шат, Хугацаа, Суралцахуйн үйл ажиллагаа, Багшийн дэмжлэг, Хэрэглэгдэхүүн)
- ТӨГСГӨЛ: Гэрийн даалгавар, Ялгаатай сурагчидтай ажиллах заавар, Багшийн дүгнэлт.

[АНХААРУУЛГА]: Суралцахуйн үйл ажиллагаа баганад сурагчдын хийх туршилт, хэлэлцүүлэг, дасгал ажил бүрийг МАШ ТОДОРХОЙ бич.
"""

# 3. Sidebar - Түүх
st.sidebar.title("🕒 Төлөвлөлт үүсгэсэн түүх")
if st.sidebar.button("➕ Шинэ төлөвлөгөө үүсгэх"):
    st.session_state.current_view = None
    st.rerun()

st.sidebar.divider()
for idx, item in enumerate(st.session_state.history):
    if st.sidebar.button(f"📄 {item['topic']} ({item['date']})", key=f"h_{idx}"):
        st.session_state.current_view = item

# 4. Үндсэн хэсэг
st.title("🎓 Багшийн туслах систем")

tab1, tab2 = st.tabs(["📝 Хичээл төлөвлөх & Econtent", "🌐 Порталууд"])

with tab1:
    col_l, col_r = st.columns([1, 1.2])

    with col_l:
        st.subheader("⚙️ Хичээлийн өгөгдөл")
        sub = st.text_input("Хичээл", "Мэдээлэл зүй")
        grd = st.selectbox("Анги", [f"{i}-р анги" for i in range(1, 13)], index=5)
        tpc = st.text_input("Хичээлийн сэдэв", placeholder="Сэдвээ оруулна уу...")
        pages = st.text_input("Сурах бичгийн хуудас", placeholder="Жишээ: 20-22")
        
        if st.button("🚀 Төлөвлөгөө боловсруулах"):
            if tpc:
                with st.spinner("AI мэргэжлийн түвшинд шинжилж байна..."):
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": SYSTEM_INSTRUCTION},
                            {"role": "user", "content": f"Хичээл: {sub}, Анги: {grd}, Сэдэв: {tpc}, Хуудас: {pages}. Сурах бичгийн агуулгаар 70/30 харьцаатай төлөвлөгөө гарга."}
                        ],
                        "temperature": 0.1 # Чанарыг улам тогтвортой болгосон
                    }
                    
                    res = requests.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        content = res.json()['choices'][0]['message']['content']
                        new_data = {
                            "date": datetime.datetime.now().strftime("%H:%M"),
                            "topic": tpc, "content": content, "sub": sub, "grd": grd
                        }
                        st.session_state.history.append(new_data)
                        st.session_state.current_view = new_data
                        st.rerun()

        st.divider()
        st.subheader("📚 Econtent Харагдац")
        st.components.v1.iframe("https://econtent.edu.mn/book", height=600)

    with col_r:
        if st.session_state.current_view:
            item = st.session_state.current_view
            st.success(f"✅ {item['topic']} - Бэлэн боллоо")
            
            # Төлөвлөгөөг харуулах
            st.markdown(item['content'])
            
            # Word файл татах
            doc = Document()
            doc.add_paragraph(item['content'])
            bio = BytesIO()
            doc.save(bio)
            st.download_button("📥 Word татах", bio.getvalue(), f"{item['topic']}.docx")
        else:
            st.info("👈 Зүүн талд сэдвээ оруулаад 'Төлөвлөгөө гаргах' товчийг дарна уу.")

with tab2:
    p_tabs = st.tabs(["EduMap", "ESIS", "Medle"])
    with p_tabs[0]: st.components.v1.iframe("https://edumap.mn/", height=800)
    with p_tabs[1]: st.components.v1.iframe("https://bagsh.esis.edu.mn/", height=800)
    with p_tabs[2]: st.components.v1.iframe("https://medle.mn/", height=800)

