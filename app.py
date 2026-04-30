import streamlit as st
import requests

# 🔹 URLs
API_URL = "https://rag-document-intelligence-system.onrender.com/ask"
UPLOAD_URL = "https://rag-document-intelligence-system.onrender.com/upload"

st.set_page_config(page_title="AI Multi-Document Assistant", layout="wide")

st.title("📄 AI Multi-Document Assistant")

# 🔹 Upload multiple PDFs
uploaded_files = st.file_uploader(
    "Upload one or more PDFs",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("Processing PDFs..."):
        try:
            files = [
                ("files", (file.name, file.getvalue(), "application/pdf"))
                for file in uploaded_files
            ]

            res = requests.post(UPLOAD_URL, files=files)

            if res.status_code == 200:
                st.success("✅ PDFs uploaded successfully")
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
user_input = st.chat_input("Ask across all uploaded PDFs...")

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

                    answer = data.get("answer", "No answer found")
                    st.markdown(answer)

                    sources = data.get("sources", [])
                    pages = data.get("pages", [])

                    if sources:
                        st.markdown("**📄 Documents:** " + ", ".join(sources))

                    if pages:
                        st.markdown("**📚 Pages:** " + ", ".join(map(str, pages)))

                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )

                else:
                    st.error("Backend error")

            except Exception as e:
                st.error(str(e))