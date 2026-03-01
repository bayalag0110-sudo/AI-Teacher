import streamlit as st
import requests
import json

# 1. Хуудасны тохиргоо
st.set_page_config(
    page_title="Ухаалаг Багшийн Туслах",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Ухаалаг Багшийн Туслах")
st.caption("AI ашиглан хичээлийн төлөвлөгөө үүсгэнэ")

# 2. AI функц
def generate_lesson_plan(topic):
    try:
        # Secrets-ээс түлхүүр унших
        if "GOOGLE_API_KEY" not in st.secrets:
            return "❌ GOOGLE_API_KEY secrets дээр тохируулаагүй байна."
            
        api_key = st.secrets["GOOGLE_API_KEY"]
        
        # Хамгийн тогтвортой V1 хаяг (404 алдаанаас сэргийлнэ)
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Чи бол туршлагатай багш. Дараах бүтэцтэйгээр Монгол хэл дээр хичээлийн төлөвлөгөө гарга: 1. Зорилго, 2. Үр дүн, 3. Хэрэглэгдэхүүн, 4. Явц, 5. Үнэлгээ. Сэдэв: {topic}"
                }]
            }]
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            data = response.json()
            if "candidates" in data:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            return "⚠️ Хариу хоосон ирлээ."
        elif response.status_code == 429:
            return "❌ Ашиглах хязгаар дууссан байна (Quota exceeded). Түр хүлээгээд дахин оролдоно уу."
        else:
            return f"❌ Алдаа: {response.status_code}\n{response.text}"

    except Exception as e:
        return f"❌ Системийн алдаа: {str(e)}"

# 3. Вэб дизайн хэсэг
topic = st.text_input("📚 Хичээлийн сэдэв оруулна уу")

col1, col2 = st.columns(2)

with col1:
    generate_btn = st.button("✨ Төлөвлөгөө үүсгэх")

with col2:
    if st.button("Sweep 🧹"):
        st.rerun()

if generate_btn:
    if not topic.strip():
        st.warning("⚠️ Сэдвээ оруулна уу.")
    else:
        with st.spinner("AI төлөвлөгөө боловсруулж байна..."):
            result = generate_lesson_plan(topic)
            st.divider()
            st.subheader("📝 Хичээлийн төлөвлөгөө")
            st.markdown(result)
