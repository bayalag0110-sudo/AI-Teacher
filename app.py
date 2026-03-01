import streamlit as st
import requests
import datetime
from docx import Document
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Medle AI - Ухаалаг Багш", layout="wide", page_icon="🎓")

# CSS тохиргоо
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    iframe { border-radius: 10px; border: 1px solid #ddd; width: 100%; }
    .history-item { padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; }
    .history-item:hover { background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# 2. Session State - Түүх болон одоогийн харагдацыг удирдах
if 'history' not in st.session_state: st.session_state.history = []
if 'current_view' not in st.session_state: st.session_state.current_view = None

# AI-д өгөх СИСТЕМ ЗААВАРЧИЛГАА (Таны Excel загварын дагуу)
SYSTEM_INSTRUCTION = """
Чи бол Монгол улсын ерөнхий боловсролын сургуулийн заах аргач багш. 
Чиний даалгавар бол хэрэглэгчийн өгсөн сэдэв болон сурах бичгийн агуулгын дагуу дараах 3 зүйлийг боловсруулах юм:

1. ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ: (Excel загварын дагуу хүснэгтээр)
2. 3-5 МИНУТЫН СОРИЛ: (Хичээлийн агуулгыг шалгах 3-5 асуулт, хариултын хамт)
3. ЯЛГААТАЙ СУРАГЧИДТАЙ АЖИЛЛАХ ЗААВАР: (Удаан сурдаг, дундаж, болон авьяаслаг сурагчдад зориулсан тусгай заавар)

[ХҮСНЭГТИЙН БҮТЭЦ]:
Заавал Markdown хүснэгт ашиглана:
| Хичээлийн үе шат | Хугацаа | Суралцахуйн үйл ажиллагаа | Багшийн дэмжлэг | Хэрэглэгдэхүүн |
"""

# 3. Sidebar - Түүхийг удирдах
st.sidebar.title("🕒 Төлөвлөгөөний түүх")
if st.sidebar.button("➕ Шинэ төлөвлөгөө эхлүүлэх"):
    st.session_state.current_view = None
    st.rerun()

st.sidebar.markdown("---")
for idx, item in enumerate(st.session_state.history):
    if st.sidebar.button(f"📄 {item['topic']} ({item['date']})", key=f"hist_{idx}"):
        st.session_state.current_view = item

# 4. Үндсэн хэсэг
st.title("🎓 Ухаалаг Багшийн Туслах")

tab_main, tab_portals = st.tabs(["📝 Хичээл боловсруулах", "🌐 Сургалтын порталууд"])

with tab_main:
    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        st.subheader("⚙️ Тохиргоо")
        sub = st.text_input("Хичээл", "Мэдээлэл зүй")
        grd = st.selectbox("Анги", [f"{i}-р анги" for i in range(1, 13)])
        tpc = st.text_input("Хичээлийн сэдэв")
        pages = st.text_input("Сурах бичгийн хуудас (Econtent)")
        
        if st.button("✨ Төлөвлөгөө + Сорил боловсруулах"):
            if tpc:
                with st.spinner("AI боловсруулж байна..."):
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    
                    user_prompt = f"Хичээл: {sub}, Анги: {grd}, Сэдэв: {tpc}, Хуудас: {pages}. Төлөвлөгөө, сорил, зааварчилгааг гарга."
                    
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": SYSTEM_INSTRUCTION},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.4
                    }
                    
                    res = requests.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        ans = res.json()['choices'][0]['message']['content']
                        new_item = {
                            "date": datetime.datetime.now().strftime("%m/%d %H:%M"),
                            "topic": tpc,
                            "content": ans,
                            "sub": sub,
                            "grd": grd
                        }
                        st.session_state.history.append(new_item)
                        st.session_state.current_view = new_item
                        st.rerun()

    with col_right:
        if st.session_state.current_view:
            item = st.session_state.current_view
            st.subheader(f"📄 Харагдац: {item['topic']}")
            st.info(f"Анги: {item['grd']} | Хичээл: {item['sub']}")
            
            # Төлөвлөгөөг харуулах
            st.markdown(item['content'])
            
            # Word файл татах
            doc = Document()
            doc.add_heading(f"{item['topic']} - Төлөвлөгөө", 0)
            doc.add_paragraph(item['content'])
            bio = BytesIO()
            doc.save(bio)
            st.download_button("📥 Word хэлбэрээр татах", bio.getvalue(), f"{item['topic']}.docx")
        else:
            st.write("👈 Зүүн талд мэдээллээ оруулаад 'Боловсруулах' товчийг дарна уу.")

with tab_portals:
    p_tab1, p_tab2, p_tab3, p_tab4 = st.tabs(["Econtent", "ESIS", "Medle"])
    with p_tab1: st.components.v1.iframe("https://econtent.edu.mn/book", height=700)
    with p_tab2: st.components.v1.iframe("https://https://edumap.mn//", height=700)
    with p_tab3: st.components.v1.iframe("https://medle.mn/", height=700)
    with p_tab4: st.components.v1.iframe("https://bagsh.esis.edu.mn/", height=700)

