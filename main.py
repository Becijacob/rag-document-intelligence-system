import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()

app = FastAPI()

# ✅ Enable CORS (frontend will call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class QueryRequest(BaseModel):
    question: str

# Global objects
vectordb = None
retriever = None
llm = ChatOpenAI(model="gpt-4o-mini")

# ✅ Root endpoint (health check)
@app.get("/")
def home():
    return {"message": "FastAPI RAG service is running"}

# ✅ Load PDF at startup
@app.on_event("startup")
def load_data():
    global vectordb, retriever

    try:
        loader = PyPDFLoader("Cloud-Based Data Processing System Architecture.pdf")
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=80
        )
        docs = splitter.split_documents(documents)

        embedding = OpenAIEmbeddings()
        vectordb = Chroma.from_documents(docs, embedding)

        retriever = vectordb.as_retriever(search_kwargs={"k": 8})

        print("✅ PDF loaded and vector DB ready")

    except Exception as e:
        print("❌ Error:", str(e))

# ✅ Main API endpoint
@app.post("/ask")
def ask_question(req: QueryRequest):
    global retriever

    try:
        # 🔥 Multi-query retrieval
        queries = [
            req.question,
            "Explain system architecture",
            "What are challenges in the system?",
            "Explain all components"
        ]

        all_docs = []

        for q in queries:
            docs = retriever.invoke(q)
            all_docs.extend(docs)

        # Remove duplicates
        unique_docs = list({doc.page_content: doc for doc in all_docs}.values())

        context = "\n".join([doc.page_content for doc in unique_docs])

        # 🔥 Strict grounding prompt
        prompt = f"""
        You are a senior system architect.

        Answer ONLY using the provided context.
        Do NOT add external knowledge.
        Structure the answer using clear headings and bullet points.

        If not found, say:
        "I don't know based on the document."

        Context:
        {context}

        Question:
        {req.question}
        """

        response = llm.invoke(prompt)

        # Sources
        pages = list(set([doc.metadata.get("page", 0) + 1 for doc in unique_docs]))

        return {
            "answer": response.content,
            "sources": sorted(pages)
        }

    except Exception as e:
        return {"error": str(e)}