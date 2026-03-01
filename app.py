import streamlit as st
import requests
import json

# API холболт
def generate_lesson_plan(subject, grade, topic, duration):
    # Хамгийн тогтвортой V1 хаяг
    api_key = st.secrets["GOOGLE_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": f"{subject} хичээлийн {grade}-д орох {topic} сэдвийн төлөвлөгөө гарга."}]}]}

    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        raise Exception(f"Алдаа: {response.status_code}, {response.text}")

# Вэб сайт
st.title("🎓 Ухаалаг Багшийн Туслах")
topic = st.text_input("Хичээлийн сэдэв")

if st.button("Хичээл төлөвлөгөө боловсруулах"):
    try:
        plan = generate_lesson_plan("Мэдээлэл технологи", "6-р анги", topic, 40)
        st.write(plan)
    except Exception as e:
        st.error(str(e))
