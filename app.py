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

# 🌟 ХАТУУ ЗААВАРЧИЛГАА (System Instruction) - ШИНЭ ЗАГВАР ДАГУУ
# Temperature 0.1 нь AI-г өөрөөсөө зохиохоос 100% сэргийлнэ.
SYSTEM_INSTRUCTION = """
Чи бол Монгол улсын Боловсролын шинжээч багш. 
Чиний даалгавар бол зөвхөн хэрэглэгчийн өгсөн СУРАХ БИЧГИЙН ТЕКСТ-д тулгуурлан 'ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ.docx' бүтцээр төлөвлөгөө гаргах.

[МӨРДӨХ ХАТУУ ДҮРЭМ]:
1. TEMPERATURE 0.1: Зөвхөн сурах бичигт байгаа дасгал, даалгавар, мэдээллийг ашигла. Юу ч зохиож болохгүй.
2. 70/30 ХАРЬЦАА: Сурагчийн идэвхтэй оролцоо 70% (унших, дасгал ажиллах), багшийн дэмжлэг 30% байна.
3. ЗАГВАРЫН БҮТЭЦ (Ягштал баримтал):
   - БАТЛАВ (Баруун дээд талд)
   - СУРГАЛТЫН МЕНЕЖЕР: .................
   - ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ (Гарчиг)
   - Анги:
   - Сар, өдөр, хугацаа:
   - Ээлжит хичээлийн сэдэв:
   - Хичээлийн зорилго:
   - Үйл явц: (Хүснэгт)
   | Хичээлийн үе шат | Хугацаа | Суралцахуйн үйл ажиллагаа | Багшийн дэмжлэг | Хэрэглэгдэхүүн |
   | :--- | :--- | :--- | :--- | :--- |
   | Эхлэл хэсэг /сэдэлжүүлэг/ | 5 мин | | | |
   | Өрнөл хэсэг /мэдлэг бүтээх/ | 25 мин | | | |
   | Төгсгөл хэсэг /дүгнэлт/ | 10 мин | | | |
   
   - Гэрийн даалгавар:
   - Ялгаатай сурагчидтай ажиллах аргачлал:
   - Нэмэлт: тухайн хичээлийн талаарх багшийн дүгнэлт:
"""

# 3. Sidebar - Төлөвлөгөөний түүх
st.sidebar.title("🕒 Боловсруулсан түүх")
for idx, item in enumerate(st.session_state.history):
    if st.sidebar.button(f"📄 {item['topic']}", key=f"h_{idx}"):
        st.session_state.current_view = item

# 4. Үндсэн цонх
st.title("👨‍🏫 Стандарт Ээлжит Хичээл Боловсруулалт")

tab1, tab2 = st.tabs(["📝 Төлөвлөгөө боловсруулах", "🌐 Сургалтын порталууд"])

with tab1:
    col_in, col_out = st.columns([1, 1.2])

    with col_in:
        st.subheader("⚙️ Оролтын өгөгдөл")
        sub = st.text_input("Хичээл", "Мэдээлэл зүй")
        grd = st.text_input("Анги", "6а")
        tpc = st.text_input("Хичээлийн сэдэв")
        
        # Линкийн хэсэг
        book_url = st.text_input("🔗 Сурах бичгийн линк (Econtent):", "https://econtent.edu.mn/book")
        st.caption("AI линкийг шууд уншихгүй тул 'Порталууд' цэснээс текстээ хуулж доор оруулна уу.")
        
        # Текст хуулах хэсэг
        content_text = st.text_area("📖 Сурах бичгийн агуулга (Текст хуулна уу):", height=300)
        
        if st.button("🚀 Загварын дагуу боловсруулах"):
            if tpc and content_text:
                with st.spinner("Зөвхөн сурах бичгийн агуулгаар боловсруулж байна..."):
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": SYSTEM_INSTRUCTION},
                            {"role": "user", "content": f"Сурах бичгийн текст: {content_text}\n\nСэдэв: {tpc}\nАнги: {grd}\nХичээл: {sub}"}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 4000
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
            
            # Word файл татах
            doc = Document()
            doc.add_paragraph(item['content'])
            bio = BytesIO()
            doc.save(bio)
            st.download_button("📥 Word татах", bio.getvalue(), f"{item['topic']}.docx")
        else:
            st.info("👈 Сурах бичгийн агуулгыг хуулж оруулаад 'Боловсруулах' дээр дарна уу.")

# 5. Порталууд - Сурах бичгийг хажууд нь нээх
with tab2:
    if book_url:
        st.components.v1.iframe(book_url, height=800, scrolling=True)
    else:
        st.info("Сурах бичгийн линк оруулна уу.")
