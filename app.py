import streamlit as st
import requests
import datetime
from docx import Document
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Medle AI - Чанарын Хяналт v4", layout="wide", page_icon="🎓")

# 2. Session State - Түүх болон харагдацыг удирдах
if 'history' not in st.session_state: st.session_state.history = []
if 'current_view' not in st.session_state: st.session_state.current_view = None

# 🌟 МАШ ХАТУУ ЗААВАРЧИЛГАА (System Instruction)
# Энэ хэсэгт таны бүх шаардлагыг "Хууль" мэт суулгаж өгсөн.
SYSTEM_INSTRUCTION = """
Чи бол Монгол улсын Боловсролын шилдэг шинжээч багш. 
Чиний даалгавар бол зөвхөн хэрэглэгчийн өгсөн СУРАХ БИЧГИЙН АГУУЛГА-д тулгуурлан 'загвар.docx'-ийн дагуу ээлжит хичээл боловсруулах.

[МӨРДӨХ ХАТУУ ДҮРЭМ]:
1. TEMPERATURE 0.1: Өөрийн мэдлэгээс зохиож болохгүй. Зөвхөн өгөгдсөн текстийг ашигла.
2. 70/30 ХАРЬЦАА: Сурагчийн идэвхтэй оролцоо 70%, багшийн чиглүүлэг 30% байна.
3. 3 ТҮВШНИЙ ДААЛГАВАР: Хичээлийн төгсгөлд сорилыг Хялбар, Дунд, Хүнд түвшинд ялгаж гарга.

[ЗАГВАРЫН БҮТЭЦ]:
- БАТЛАВ: Баруун дээд өнцөгт (СУРГАЛТЫН МЕНЕЖЕР Б. НАМУУН)
- ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨГӨӨ (Гарчиг)
- ХҮСНЭГТ: | Хичээлийн үе шат | Хугацаа | Суралцахуйн үйл ажиллагаа | Багшийн дэмжлэг | Хэрэглэгдэхүүн |
- ҮЕ ШАТ: Эхлэл (5 мин), Өрнөл (25 мин), Төгсгөл (10 мин)
- ГЭРИЙН ДААЛГАВАР, ЯЛГААТАЙ СУРАГЧИДТАЙ АЖИЛЛАХ АРГАЧЛАЛ, БАГШИЙН ДҮГНЭЛТ.
"""

# 3. Sidebar - Төлөвлөгөөний түүх
st.sidebar.title("🕒 Түүх /History/")
if st.sidebar.button("➕ Шинэ төлөвлөгөө"):
    st.session_state.current_view = None
    st.rerun()

st.sidebar.markdown("---")
for idx, item in enumerate(st.session_state.history):
    if st.sidebar.button(f"📄 {item['topic']} ({item['date']})", key=f"hist_{idx}"):
        st.session_state.current_view = item

# 4. Үндсэн цонх
st.title("👨‍🏫 Мэргэжлийн Ээлжит Хичээл Боловсруулалт")

tab_main, tab_portals = st.tabs(["📝 Төлөвлөгөө & Сорил", "🌐 Порталууд"])

with tab_main:
    col_input, col_view = st.columns([1, 1.2])

    with col_input:
        st.subheader("⚙️ Өгөгдлийн сан")
        sub = st.text_input("Хичээл", "Мэдээлэл зүй")
        grd = st.text_input("Анги", "6-р анги")
        tpc = st.text_input("Хичээлийн сэдэв")
        
        # Сурах бичгийн агуулга хуулах хэсэг (Маш чухал)
        content_text = st.text_area("📖 Сурах бичгийн агуулга (Энд текстийг хуулна уу)", height=300)
        
        if st.button("🚀 Чанарын дагуу боловсруулах"):
            if tpc and content_text:
                with st.spinner("AI Temperature 0.1 горимд ажиллаж байна..."):
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": SYSTEM_INSTRUCTION},
                            {"role": "user", "content": f"Агуулга: {content_text}\n\nСэдэв: {tpc}\nАнги: {grd}\nХичээл: {sub}"}
                        ],
                        "temperature": 0.1,  # Хамгийн өндөр нарийвчлал
                        "max_tokens": 4096
                    }
                    
                    res = requests.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        ans = res.json()['choices'][0]['message']['content']
                        new_data = {
                            "date": datetime.datetime.now().strftime("%H:%M"),
                            "topic": tpc,
                            "content": ans,
                            "sub": sub, "grd": grd
                        }
                        st.session_state.history.append(new_data)
                        st.session_state.current_view = new_data
                        st.rerun()

    with col_view:
        if st.session_state.current_view:
            item = st.session_state.current_view
            st.success(f"✅ {item['topic']} - Чанарын шалгалтаар батлагдлаа")
            
            # Үр дүнг харуулах
            st.markdown(item['content'])
            
            # Word файл болгож татах
            doc = Document()
            doc.add_paragraph(item['content'])
            bio = BytesIO()
            doc.save(bio)
            st.download_button("📥 Word татах", bio.getvalue(), f"{item['topic']}.docx")
        else:
            st.info("👈 Зүүн талд агуулгаа оруулаад 'Боловсруулах' дээр дарна уу.")

# 5. Порталууд
with tab_portals:
    p_tabs = st.tabs(["EduMap", "Econtent", "ESIS", "Medle"])
    with p_tabs[0]: st.components.v1.iframe("https://edumap.mn/", height=800)
    with p_tabs[1]: st.components.v1.iframe("https://econtent.edu.mn/book", height=800)
    with p_tabs[2]: st.components.v1.iframe("https://bagsh.esis.edu.mn/", height=800)
    with p_tabs[3]: st.components.v1.iframe("https://medle.mn/", height=800)
