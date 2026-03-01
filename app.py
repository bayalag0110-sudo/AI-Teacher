import streamlit as st
import requests
import json

st.title("🎓 Ухаалаг Багшийн Туслах")

def generate_lesson_plan(topic):
    # Secrets-ээс түлхүүрийг унших
    api_key = st.secrets["GOOGLE_API_KEY"]
    
    # Хамгийн тогтвортой V1 хаяг
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": f"Чи бол туршлагатай багш. '{topic}' сэдвээр хичээлийн төлөвлөгөөг Монгол хэл дээр гарга."}]
        }]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        # Алдаа гарвал дэлгэрэнгүй харуулна
        return f"Алдаа гарлаа: {response.status_code} - {response.text}"

topic = st.text_input("Хичээлийн сэдэв:")

if st.button("Хичээл төлөвлөгөө боловсруулах"):
    if topic:
        with st.spinner("AI ажиллаж байна..."):
            result = generate_lesson_plan(topic)
            st.markdown("### 📝 Төлөвлөгөө:")
            st.write(result)
    else:
        st.warning("Сэдвээ оруулна уу.")
