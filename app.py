import streamlit as st
import requests
import datetime
from docx import Document
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Medle AI - Заах Аргач", layout="wide", page_icon="🎓")

# CSS - Загвар болон Iframe тохиргоо
st.markdown("""
    <style>
    iframe { border-radius: 10px; border: 1px solid #ddd; width: 100%; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745; }
    .sidebar-text { font-size: 14px; color: #666; }
    </style>
    """, unsafe_allow_html=True)

# 2. Session State - Түүх болон харагдацыг удирдах
if 'history' not in st.session_state: st.session_state.history = []
if 'current_view' not in st.session_state: st.session_state.current_view = None

# 3. Sidebar - Төлөвлөгөөний түүх
st.sidebar.title("🕒 Төлөвлөгөөний түүх")
if st.sidebar.button("➕ Шинэ төлөвлөгөө эхлүүлэх"):
    st.session_state.current_view = None
    st.rerun()

st.sidebar.markdown("---")
for idx, item in enumerate(st.session_state.history):
    if st.sidebar.button(f"📄 {item['topic']} ({item['date']})", key=f"hist_{idx}"):
        st.session_state.current_view = item

# 4. Үндсэн цонх
st.title("🎓 Ухаалаг Багшийн Систем (Заах аргач v2.0)")

tab_main, tab_portals = st.tabs(["📝 Хичээл боловсруулах", "🌐 Сургалтын порталууд"])

with tab_main:
    col_input, col_result = st.columns([1, 1.2])

    with col_input:
        st.subheader("⚙️ Төлөвлөлтийн тохиргоо")
        sub = st.text_input("Хичээл", "Мэдээлэл зүй")
        grd = st.selectbox("Анги", [f"{i}-р анги" for i in range(1, 13)])
        tpc = st.text_input("Хичээлийн сэдэв", placeholder="Жишээ: Мэдээлэл гэж юу вэ?")
        pages = st.text_input("Сурах бичгийн хуудас", placeholder="Жишээ: 12-15")
        
        if st.button("✨ Чанартай боловсруулах"):
            if tpc:
                with st.spinner("Заах аргач AI боловсруулж байна..."):
                    # API холболтын тохиргоо
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    
                    # 🚀 ЭНЭ ХЭСЭГ БОЛ PAYLOAD (Таны хүссэн 70/30 дүрэм орсон хэсэг)
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {
                                "role": "system", 
                                "content": """Чи бол Монгол улсын 'Заах аргач багш'. Чиний даалгавар бол:
                                1. ИДЭВХТЭЙ СУРАЛЦАХУЙ: Хичээлийн үе шат бүрт сурагчийн идэвхтэй оролцоог (Active Learning) 70%, багшийн тайлбарыг 30% байхаар төлөвлө.
                                2. 3 ТҮВШНИЙ ДААЛГАВАР: Хичээлтэй холбоотой сорилыг Хялбар, Дунд, Хүнд гэсэн 3 түвшинд ялгаж гарга.
                                3. СТАНДАРТ ЗАГВАР: 'загвар ээлжит.xlsx' бүтцийн дагуу: Зорилго, Үйл явцын хүснэгт, Гэрийн даалгавар, Ялгаатай сурагчидтай ажиллах зааврыг заавал бич.
                                4. ХҮСНЭГТ: Markdown хүснэгт ашиглан (Хугацаа, Суралцахуйн үйл ажиллагаа, Багшийн дэмжлэг, Хэрэглэгдэхүүн) багануудыг дэлгэрэнгүй бөглө."""
                            },
                            {
                                "role": "user", 
                                "content": f"Хичээл: {sub}, Анги: {grd}, Сэдэв: {tpc}, Хуудас: {pages}. Сурах бичгийн агуулгыг ашиглан чанартай төлөвлөгөө гарга."
                            }
                        ],
                        "temperature": 0.4,
                        "max_tokens": 4096
                    }
                    
                    try:
                        res = requests.post(url, headers=headers, json=payload)
                        if res.status_code == 200:
                            ans = res.json()['choices'][0]['message']['content']
                            # Түүхэнд хадгалах
                            new_entry = {
                                "date": datetime.datetime.now().strftime("%m/%d %H:%M"),
                                "topic": tpc,
                                "content": ans,
                                "sub": sub, "grd": grd
                            }
                            st.session_state.history.append(new_entry)
                            st.session_state.current_view = new_entry
                            st.rerun()
                        else:
                            st.error(f"Алдаа гарлаа: {res.status_code}")
                    except Exception as e:
                        st.error(f"Холболтын алдаа: {str(e)}")
            else:
                st.warning("⚠️ Сэдвийн нэрийг оруулна уу.")

    with col_result:
        if st.session_state.current_view:
            item = st.session_state.current_view
            st.subheader(f"📄 {item['topic']}")
            st.info(f"📚 {item['sub']} | {item['grd']}")
            
            # AI-ийн хариултыг харуулах
            st.markdown(item['content'])
            
            # Word файл болгох
            doc = Document()
            doc.add_heading(f"Ээлжит хичээл: {item['topic']}", 0)
            doc.add_paragraph(item['content'])
            bio = BytesIO()
            doc.save(bio)
            st.download_button("📥 Word татах", bio.getvalue(), f"{item['topic']}.docx")
        else:
            st.info("👈 Зүүн талд мэдээллээ оруулаад 'Чанартай боловсруулах' товчийг дарна уу.")

# 5. Порталуудын хэсэг (EduMap нэмэгдсэн)
with tab_portals:
    p_tabs = st.tabs(["Econtent", "EduMap", "ESIS", "Medle"])
    with p_tabs[0]: st.components.v1.iframe("https://econtent.edu.mn/book", height=800)
    with p_tabs[1]: st.components.v1.iframe("https://edumap.mn/", height=800)
    with p_tabs[2]: st.components.v1.iframe("https://bagsh.esis.edu.mn/", height=800)
    with p_tabs[3]: st.components.v1.iframe("https://medle.mn/", height=800)
