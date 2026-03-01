import streamlit as st
import requests
import json

st.set_page_config(page_title="Ухаалаг Багшийн Туслах", page_icon="🎓")
st.title("🎓 Ухаалаг Багшийн Туслах")

def generate_lesson_plan(topic):
    try:
        # 1. Түлхүүрийг эхэлж уншина
        if "GOOGLE_API_KEY" not in st.secrets:
            return "❌ Secrets хэсэгт GOOGLE_API_KEY-ээ тохируулаарай."
        
        api_key = st.secrets["GOOGLE_API_KEY"]
        
        # 2. Түлхүүр уншсаны дараа URL-аа үүсгэнэ (v1 ашиглав)
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": f"Чи бол багш. '{topic}' сэдвээр Монгол хэл дээр хичээлийн төлөвлөгөө гарга."}]
            }]
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Алдаа: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Системийн алдаа: {str(e)}"

topic = st.text_input("📚 Хичээлийн сэдэв:")

if st.button("✨ Төлөвлөгөө үүсгэх"):
    if topic:
        with st.spinner("AI ажиллаж байна..."):
            result = generate_lesson_plan(topic)
            st.markdown("---")
            st.markdown(result)
