import streamlit as st
import requests
import datetime
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Medle AI - Багшийн Төв", layout="wide", page_icon="🎓")

# CSS - Орчин үеийн загвар ба Iframe тохиргоо
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 5px; padding: 10px; }
    iframe { border-radius: 10px; border: 1px solid #ddd; width: 100%; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

# 2. Түүх болон Статистик хадгалах
if 'history' not in st.session_state: st.session_state.history = []
if 'teacher_emails' not in st.session_state: st.session_state.teacher_emails = set()

# AI-д өгөх СИСТЕМ ЗААВАРЧИЛГАА (Таны Excel загварын дагуу)
SYSTEM_INSTRUCTION = """
Чи бол Монгол улсын ерөнхий боловсролын сургуулийн заах аргач багш. 
Чиний даалгавар бол хэрэглэгчийн өгсөн сэдэв болон сурах бичгийн агуулгын дагуу 'ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ' боловсруулах юм.

[МӨРДӨХ СТАНДАРТ]:
- 'Хичээлийн зорилго'-ыг Блүүмийн таксономийн дагуу тодорхойлно.
- Хичээлийн үе шат бүрийг (Эхлэл, Өрнөл, Төгсгөл) маш тодорхой, сурагч төвтэй байхаар бичнэ.
- 'Суралцахуйн үйл ажиллагаа' хэсэгт багш юу хийх, сурагч юу хийхийг заавал тусгана.
- 'Багшийн дэмжлэг' хэсэгт чиглүүлэх асуултууд болон хүүхэд бүртэй хэрхэн ажиллахыг бичнэ.
- Төгсгөлд нь 'Ялгаатай сурагчидтай ажиллах аргачлал' болон 'Багшийн дүгнэлт' хэсгийг заавал оруулна.

[ХҮСНЭГТИЙН БҮТЭЦ]:
Заавал Markdown хүснэгт ашиглана:
| Хичээлийн үе шат | Хугацаа | Суралцахуйн үйл ажиллагаа | Багшийн дэмжлэг | Хэрэглэгдэхүүн |
| :--- | :--- | :--- | :--- | :--- |
"""

# 3. Нэвтрэх хэсэг
def login():
    st.sidebar.title("🔐 Багшийн нэвтрэх")
    email = st.sidebar.text_input("Эмайл (@medle.mn)")
    password = st.sidebar.text_input("Нууц үг", type="password")
    if st.sidebar.button("Системд нэвтрэх"):
        if email.strip().lower().endswith("@medle.mn") and password:
            st.session_state.logged_in = True
            st.session_state.user_email = email.strip().lower()
            st.session_state.teacher_emails.add(email.strip().lower())
            st.rerun()
        else:
            st.sidebar.error("❌ Зөвхөн @medle.mn хаяг!")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🎓 Medle AI - Ухаалаг Багшийн Систем")
    c1, c2 = st.columns(2)
    c1.metric("Нийт боловсруулсан", len(st.session_state.history))
    c2.metric("Багш нарын тоо", len(st.session_state.teacher_emails))
    login()
    st.stop()

# 4. Sidebar - Түүх харуулах
st.sidebar.success(f"👤 {st.session_state.user_email}")
with st.sidebar.expander("🕒 Төлөвлөгөөний түүх"):
    if not st.session_state.history:
        st.write("Түүх байхгүй.")
    else:
        for item in st.session_state.history:
            st.caption(f"{item['date']} - {item['topic']}")

if st.sidebar.button("Гарах"):
    st.session_state.logged_in = False
    st.rerun()

# 5. Үндсэн табууд (Бүх сайтууд ил харагдана)
tab_main, tab_esis, tab_edumap, tab_bagsh, tab_medle = st.tabs([
    "📝 Хичээл төлөвлөх & Econtent", 
    "📊 ESIS", "🗺️ EduMap", "👨‍🏫 Багшийн хөгжил", "💻 Medle.mn"
])

# --- TAB 1: ECONTENT БА AI ТӨЛӨВЛӨГӨӨ ---
with tab_main:
    col_book, col_plan = st.columns([1.2, 1])
    
    with col_book:
        st.subheader("📚 Сурах бичиг")
        book_url = st.text_input("Econtent линк:", "https://econtent.edu.mn/book/12bek/1")
        st.components.v1.iframe(book_url, height=700, scrolling=True)
    
    with col_plan:
        st.subheader("⚙️ Шинэ төлөвлөгөө")
        sub = st.text_input("Хичээл", "Мэдээлэл зүй")
        grd = st.selectbox("Анги", [f"{i}-р анги" for i in range(1, 13)])
        tpc = st.text_input("Сэдэв (Номын агуулгын дагуу)")
        pages = st.text_input("Ашиглах хуудас (Жишээ: 45-48)")
        
        if st.button("✨ Төлөвлөгөө боловсруулах"):
            if tpc and pages:
                with st.spinner("AI стандартын дагуу боловсруулж байна..."):
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    
                    user_prompt = f"Хичээл: {sub}, Анги: {grd}, Сэдэв: {tpc}, Номын хуудас: {pages}. Сурах бичгийн энэ хуудасны агуулгын хүрээнд төлөвлөгөөг гарга."
                    
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
                        st.session_state.history.append({"date": str(datetime.date.today()), "topic": tpc, "content": ans})
                        st.markdown(ans)
                        
                        # Word татах
                        doc = Document()
                        doc.add_heading('ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ', 0)
                        doc.add_paragraph(ans)
                        bio = BytesIO()
                        doc.save(bio)
                        st.download_button("📥 Word татах", bio.getvalue(), f"{tpc}.docx")
                    else:
                        st.error("AI холболтод алдаа гарлаа.")
            else:
                st.warning("Сэдэв болон хуудсаа оруулна уу.")

# --- БУСАД ПОРТАЛУУДЫН IFRAME ХЭСЭГ ---
with tab_esis:
    st.components.v1.iframe("https://bagsh.esis.edu.mn/", height=800, scrolling=True)

with tab_edumap:
    st.components.v1.iframe("https://edumap.mn/", height=800, scrolling=True)

with tab_bagsh:
    st.components.v1.iframe("https://bagsh.edu.mn/", height=800, scrolling=True)

with tab_medle:
    st.components.v1.iframe("https://medle.mn/", height=800, scrolling=True)
