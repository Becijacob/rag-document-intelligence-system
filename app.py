import streamlit as st
import requests

# 🔹 Page config
st.set_page_config(page_title="AI Document Assistant", layout="wide")

# 🔹 Title
st.title("📄 AI Document Assistant (FastAPI + RAG)")
st.write("Ask questions about your document")

# 🔹 Input box
query = st.text_input("Ask a question")

# 🔹 Button (optional but useful)
ask_button = st.button("Ask")

# 🔹 Trigger on button OR enter
if query and ask_button:

    with st.spinner("🔍 Generating answer... Please wait"):
        try:
            # 🔥 Call FastAPI backend
            response = requests.post(
                "https://rag-backend.onrender.com/ask",
                json={"question": query},
                timeout=30
            )

            # 🔹 Check response status
            if response.status_code != 200:
                st.error("❌ API Error. Please check backend.")
            else:
                result = response.json()

                # 🔹 Display answer
                st.markdown("### ✅ Answer")
                st.write(result.get("answer", "No answer found"))

                st.divider()

                # 🔹 Display sources
                st.markdown("### 📚 Sources")
                sources = result.get("sources", [])

                if sources:
                    st.write(", ".join([f"Page {p}" for p in sources]))
                else:
                    st.write("No sources found")

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to FastAPI backend. Is it running?")
        except requests.exceptions.Timeout:
            st.error("⏳ Request timed out. Try again.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")