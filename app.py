import streamlit as st
import requests
import datetime
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Medle AI - Багшийн Төв", layout="wide", page_icon="🎓")

# CSS - Орчин үеийн загвар
st.markdown("""
    <style>
    .link-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 10px; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .history-card { background-color: #ffffff; padding: 10px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Түүх болон Статистик хадгалах (Session State)
if 'history' not in st.session_state: st.session_state.history = []
if 'teacher_emails' not in st.session_state: st.session_state.teacher_emails = set()

# 3. Нэвтрэх хэсэг
def login():
    st.sidebar.title("🔐 Нэвтрэх")
    email = st.sidebar.text_input("Эмайл (@medle.mn)")
    password = st.sidebar.text_input("Нууц үг", type="password")
    if st.sidebar.button("Нэвтрэх"):
        if email.strip().lower().endswith("@medle.mn") and password:
            st.session_state.logged_in = True
            st.session_state.user_email = email.strip().lower()
            st.session_state.teacher_emails.add(email.strip().lower())
            st.rerun()
        else:
            st.sidebar.error("❌ Зөвхөн @medle.mn хаяг зөвшөөрөгдөнө!")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🎓 Medle AI - Ухаалаг Багшийн Систем")
    c1, c2 = st.columns(2)
    c1.metric("Нийт боловсруулсан", len(st.session_state.history))
    c2.metric("Систем дэх багш нар", len(st.session_state.teacher_emails))
    login()
    st.stop()

# 4. Үндсэн цэс болон Sidebar
st.sidebar.success(f"👤 {st.session_state.user_email}")
if st.sidebar.button("Системээс гарах"):
    st.session_state.logged_in = False
    st.rerun()

# 5. НҮҮР ХУУДАС - СУРГАЛТЫН САЙТУУДЫН ЖАГСААЛТ
st.title("🌐 Сургалтын нэгдсэн порталууд")
links = {
    "📊 ESIS систем": "https://bagsh.esis.edu.mn/",
    "👨‍🏫 Багшийн хөгжил": "https://bagsh.edu.mn/",
    "🗺️ EduMap": "https://edumap.mn/",
    "📚 Цахим сурах бичиг": "https://econtent.edu.mn/book",
    "💻 Medle Цахим сургууль": "https://medle.mn/"
}

cols = st.columns(len(links))
for i, (name, url) in enumerate(links.items()):
    with cols[i]:
        st.markdown(f"""<div class='link-card'><b>{name}</b><br><a href='{url}' target='_blank'>Шууд нээх</a></div>""", unsafe_allow_html=True)

st.divider()

# 6. ЭЭЛЖИТ ХИЧЭЭЛ ТӨЛӨВЛӨХ & ТҮҮХ
col_main, col_hist = st.columns([2, 1])

with col_main:
    st.subheader("📝 Шинэ хичээл төлөвлөх")
    c_a, c_b = st.columns(2)
    with c_a:
        sub = st.text_input("Хичээл", "Мэдээлэл зүй")
        grd = st.selectbox("Анги", [f"{i}-р анги" for i in range(1, 13)])
    with c_b:
        tpc = st.text_input("Хичээлийн сэдэв")
        dur = st.number_input("Хугацаа (мин)", 40)

    if st.button("✨ Төлөвлөгөө боловсруулах"):
        if tpc:
            with st.spinner("AI боловсруулж байна..."):
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                # Таны ирүүлсэн албан ёсны загварын дагуу зааварчилгаа
                prompt = f"""Монгол улсын ээлжит хичээлийн төлөвлөлтийн загвараар {sub} хичээлийн {grd}-ийн '{tpc}' сэдвийг Эхлэл, Өрнөл, Төгсгөл үе шаттай, хүснэгт хэлбэрээр боловсруулж өг.
                Хүснэгтийн багана бүрийг (Хугацаа, Суралцахуйн үйл ажиллагаа, Багшийн дэмжлэг, Хэрэглэгдэхүүн) тодорхой бич."""
                
                res = requests.post(url, headers=headers, json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}]
                })
                
                if res.status_code == 200:
                    result = res.json()['choices'][0]['message']['content']
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Түүхэнд хадгалах
                    st.session_state.history.insert(0, {"date": now, "topic": tpc, "content": result})
                    st.success("Амжилттай боловсруулагдлаа!")
                    st.markdown(result)
                    
                    # Word файл үүсгэх
                    doc = Document()
                    doc.add_heading('ЭЭЛЖИТ ХИЧЭЭЛИЙН ТӨЛӨВЛӨЛТ', 0)
                    doc.add_paragraph(f"Сэдэв: {tpc}\nХичээл: {sub}\nАнги: {grd}\nОгноо: {now}")
                    doc.add_paragraph(result)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button("📥 Word татах", bio.getvalue(), f"{tpc}.docx")
        else:
            st.warning("Сэдвээ оруулна уу.")

with col_hist:
    st.subheader("🕒 Боловсруулсан түүх")
    if not st.session_state.history:
        st.write("Түүх байхгүй байна.")
    else:
        for item in st.session_state.history:
            with st.expander(f"{item['date']} - {item['topic']}"):
                st.markdown(item['content'])
                # Түүхээс Word татах боломж
                h_doc = Document()
                h_doc.add_paragraph(item['content'])
                h_bio = BytesIO()
                h_doc.save(h_bio)
                st.download_button("📥 Татах", h_bio.getvalue(), f"{item['topic']}.docx", key=item['date'])
