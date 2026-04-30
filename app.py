import streamlit as st
import requests

# 🔹 Page config
st.set_page_config(page_title="AI Document Assistant", layout="wide")

# 🔹 Backend URL
API_URL = "https://rag-document-intelligence-system.onrender.com/ask"

# 🔹 Title
st.title("📄 AI Document Assistant (FastAPI + RAG)")
st.write("Ask questions about your document")

# 🔹 Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🔹 Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 🔹 Chat input
query = st.chat_input("Ask a question...")

# 🔹 When user sends message
if query:

    # Save user message
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Generating answer... Please wait"):

            try:
                response = requests.post(
                    API_URL,
                    json={"question": query},
                    timeout=60
                )

                # 🔹 Debug info
                st.caption(f"Status Code: {response.status_code}")

                if response.status_code != 200:
                    error_msg = "❌ Backend returned error"
                    st.error(error_msg)
                    st.write(response.text)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                    st.stop()

                data = response.json()

                answer = data.get("answer", "No answer found")

                # 🔹 Show answer
                st.markdown(answer)

                # 🔹 Show sources
                sources = data.get("sources", [])
                if sources:
                    st.markdown("**📚 Sources:** " + ", ".join([f"Page {p}" for p in sources]))

                # 🔹 Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except requests.exceptions.ConnectionError:
                error_msg = "❌ Cannot connect to backend"
                st.error(error_msg)
                st.info("👉 Check if Render service is running")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

            except requests.exceptions.Timeout:
                error_msg = "⏳ Request timed out"
                st.error(error_msg)
                st.info("👉 First request may take ~1 min (Render cold start). Try again")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

            except Exception as e:
                error_msg = f"⚠️ Unexpected Error: {e}"
                st.error(error_msg)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })