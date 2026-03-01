import streamlit as st
import requests
import datetime
from docx import Document
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Medle AI - Чанарын Хяналт", layout="wide", page_icon="🎓")

# 2. Session State удирдлага
if 'history' not in st.session_state: st.session_state.history = []
if 'current_view' not in st.session_state: st.session_state.current_view = None

# 🌟 ХАТУУ ЗААВАРЧИЛГАА (System Instruction) - ЗАГВАР.DOCX ДАГУУ
SYSTEM_INSTRUCTION = """
Чи бол Монгол улсын Боловсролын шилдэг шинжээч багш. 
Чиний даалгавар бол зөвхөн хэрэглэгчийн өгсөн СУРАХ БИЧГИЙН АГУУЛГА-д тулгуурлан 'загвар.docx'-ийн дагуу ээлжит хичээл боловсруулах.

[МӨРДӨХ ХАТУУ ДҮРЭМ]:
1. TEMPERATURE 0.1: Хэзээ ч өөрөөсөө мэдээлэл зохиож болохгүй. Зөвхөн өгөгдсөн текстийг ашигла.
2. 70/30 ХАРЬЦАА: Сурагчийн идэвхтэй оролцоо 70% (текст унших, дасгал ажиллах, хэлэлцэх), багшийн чиглүүлэг 30% байна.
3. 3 ТҮВШНИЙ ДААЛГАВАР: Хичээлийн төгсгөлд сорилыг Хялбар, Дунд, Хүнд түвшинд ялгаж гарга.

[ЗАГВАРЫН БҮТЭЦ]:
- БАТЛАВ: Баруун дээд өнцөгт (СУРГАЛТЫН МЕНЕЖЕР Б. НАМУУН)
- ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨГӨӨ (Гарчиг)
- ХҮСНЭГТ: | Хичээлийн үе шат | Хугацаа | Суралцахуйн үйл ажиллагаа | Багшийн дэмжлэг | Хэрэрлэгдэхүүн |
- ҮЕ ШАТ: Эхлэл (5 мин), Өрнөл (25 мин), Төгсгөл (10 мин)
- ГЭРИЙН ДААЛГАВАР, ЯЛГААТАЙ СУРАГЧИДТАЙ АЖИЛЛАХ АРГАЧЛАЛ, БАГШИЙН ДҮГНЭЛТ.
"""

# 3. Sidebar - Түүх
st.sidebar.title("🕒 Боловсруулсан түүх")
for idx, item in enumerate(st.session_state.history):
    if st.sidebar.button(f"📄 {item['topic']}", key=f"h_{idx}"):
        st.session_state.current_view = item

# 4. Үндсэн цонх
st.title("👨‍🏫 Сурах бичгийн агуулгаар төлөвлөх")

tab1, tab2 = st.tabs(["📝 Төлөвлөгөө боловсруулах", "🌐 Порталууд"])

with tab1:
    col_in, col_out = st.columns([1, 1.2])

    with col_in:
        st.subheader("⚙️ Оролтын мэдээлэл")
        sub = st.text_input("Хичээл", "Мэдээлэл зүй")
        tpc = st.text_input("Хичээлийн сэдэв")
        
        # Линкийн хэсэг
        book_link = st.text_input("🔗 Сурах бичгийн линк (Econtent):", "https://econtent.edu.mn/book")
        st.caption("AI линк доторх текстийг шууд унших боломжгүй тул доорх цонхонд текстийг хуулж өгнө үү.")
        
        # Текст хуулах (AI үүн дээр үндэслэн ажиллана)
        content_text = st.text_area("📖 Линк доторх текстийг энд хуулж оруулна уу:", height=250)
        
        if st.button("🚀 Чанартай боловсруулах (Temp 0.1)"):
            if tpc and content_text:
                with st.spinner("Зөвхөн сурах бичгийн агуулгаар боловсруулж байна..."):
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": SYSTEM_INSTRUCTION},
                            {"role": "user", "content": f"Сурах бичгийн агуулга: {content_text}\n\nСэдэв: {tpc}\nХичээл: {sub}"}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 4096
                    }
                    
                    res = requests.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        ans = res.json()['choices'][0]['message']['content']
                        new_item = {"date": datetime.datetime.now().strftime("%H:%M"), "topic": tpc, "content": ans}
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
            st.info("👈 Линкээ нээж, текстийг хуулж оруулаад 'Боловсруулах' товчийг дарна уу.")

# 5. Порталууд (Iframe ашиглан линкийг хажууд нь нээх)
with tab2:
    if book_link:
        st.components.v1.iframe(book_link, height=800, scrolling=True)
    else:
        st.write("Линк оруулна уу.")
