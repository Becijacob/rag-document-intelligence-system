import streamlit as st
import requests

# 🔹 Page config
st.set_page_config(page_title="AI Document Assistant", layout="wide")

# 🔹 Backend URL (IMPORTANT → replace if needed)
API_URL = "https://rag-backend.onrender.com/ask"

# 🔹 Title
st.title("📄 AI Document Assistant (FastAPI + RAG)")
st.write("Ask questions about your document")

# 🔹 Input
query = st.text_input("Ask a question")

# 🔹 Button
if st.button("Ask"):

    if not query:
        st.warning("⚠️ Please enter a question")
        st.stop()

    with st.spinner("🔍 Generating answer... Please wait"):

        try:
            response = requests.post(
                API_URL,
                json={"question": query},
                timeout=60   # ⬅️ increased timeout (Render is slow first time)
            )

            # 🔹 Debug info (VERY IMPORTANT)
            st.caption(f"Status Code: {response.status_code}")

            if response.status_code != 200:
                st.error("❌ Backend returned error")
                st.write(response.text)   # show real error
                st.stop()

            data = response.json()

            # 🔹 Show answer
            st.markdown("### ✅ Answer")
            st.write(data.get("answer", "No answer found"))

            # 🔹 Show sources (if available)
            sources = data.get("sources", [])

            if sources:
                st.markdown("### 📚 Sources")
                st.write(", ".join([f"Page {p}" for p in sources]))

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend")
            st.info("👉 Check if Render service is running")

        except requests.exceptions.Timeout:
            st.error("⏳ Request timed out")
            st.info("👉 First request may take ~1 min (Render cold start). Try again")

        except Exception as e:
            st.error(f"⚠️ Unexpected Error: {e}")