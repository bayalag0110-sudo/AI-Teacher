import streamlit as st
import requests

st.set_page_config(
    page_title="Ухаалаг Багшийн Туслах",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Ухаалаг Багшийн Туслах")
st.caption("AI ашиглан хичээлийн төлөвлөгөө үүсгэнэ")

url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"

def generate_lesson_plan(topic):
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""
Чи бол туршлагатай багш.

Дараах бүтэцтэйгээр Монгол хэл дээр хичээлийн төлөвлөгөө гарга:

1. Хичээлийн зорилго
2. Суралцах үр дүн
3. Хэрэглэгдэхүүн
4. Хичээлийн явц (алхамчилсан)
5. Үнэлгээний арга

Сэдэв: {topic}
"""
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            f"{API_URL}?key={api_key}",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()

            if "candidates" in data:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return "⚠️ Хариу хоосон ирлээ."

        elif response.status_code == 403:
            return "❌ API key зөвшөөрөлгүй байна (403)."

        elif response.status_code == 404:
            return "❌ Model олдсонгүй (404)."

        else:
            return f"❌ Алдаа: {response.status_code}\n{response.text}"

    except requests.exceptions.Timeout:
        return "⏱️ Хэт удаан хариу өглөө (timeout)."

    except KeyError:
        return "❌ GOOGLE_API_KEY secrets дээр алга."

    except Exception as e:
        return f"❌ Системийн алдаа: {str(e)}"


topic = st.text_input("📚 Хичээлийн сэдэв оруулна уу")

col1, col2 = st.columns([1,1])

with col1:
    generate_btn = st.button("✨ Төлөвлөгөө үүсгэх")

with col2:
    clear_btn = st.button("🧹 Цэвэрлэх")

if clear_btn:
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



