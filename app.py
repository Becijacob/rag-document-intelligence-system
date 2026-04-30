import streamlit as st
import requests

# 🔹 URLs
API_URL = "https://rag-document-intelligence-system.onrender.com/ask"
UPLOAD_URL = "https://rag-document-intelligence-system.onrender.com/upload"

st.set_page_config(page_title="AI Document Assistant", layout="wide")

st.title("📄 AI Document Assistant (Upload + Chat)")

# 🔹 Upload PDF
uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file:
    with st.spinner("Uploading and processing..."):
        try:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf"
                )
            }

            res = requests.post(UPLOAD_URL, files=files)

            if res.status_code == 200:
                st.success("✅ PDF uploaded successfully")
            else:
                st.error("❌ Upload failed")

        except Exception as e:
            st.error(f"Upload error: {e}")

# 🔹 Chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🔹 Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 🔹 Input
user_input = st.chat_input("Ask a question about your PDF...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"question": user_input},
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer")

                    st.markdown(answer)

                    sources = data.get("sources", [])
                    if sources:
                        st.markdown(
                            "**📚 Sources:** " + ", ".join([f"Page {p}" for p in sources])
                        )

                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )

                else:
                    st.error("Backend error")

            except Exception as e:
                st.error(str(e))