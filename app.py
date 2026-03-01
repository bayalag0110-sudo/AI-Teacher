def generate_lesson_plan(topic):
    api_key = st.secrets["GOOGLE_API_KEY"]
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": f"Чи бол туршлагатай багш. '{topic}' сэдвээр хичээлийн төлөвлөгөөг Монгол хэл дээр гарга."}]
        }]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Алдаа гарлаа: {response.status_code} - {response.text}"
