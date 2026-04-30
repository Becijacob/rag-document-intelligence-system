import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# 🔹 Load env variables
load_dotenv()

app = FastAPI()

# 🔹 Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Request schema
class QueryRequest(BaseModel):
    question: str

# 🔹 Global objects
vectordb = None
retriever = None
llm = None

# 🔹 Root endpoint
@app.get("/")
def home():
    return {"message": "FastAPI RAG service is running"}

# 🔹 Debug endpoint
@app.get("/check")
def check_key():
    key = os.getenv("OPENAI_API_KEY")
    return {
        "key_present": key is not None,
        "key_length": len(key) if key else 0
    }

# 🔹 Startup loader
@app.on_event("startup")
def load_data():
    global vectordb, retriever, llm

    try:
        print("🚀 Starting backend setup...")

        # ✅ Check API Key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("❌ OPENAI_API_KEY is missing in environment")

        # ✅ Initialize LLM
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        # ✅ Load PDF
        # pdf_path = "Cloud-Based Data Processing System Architecture.pdf"

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        pdf_path = os.path.join(
            BASE_DIR,
            "Cloud_Based.pdf"
        )

        print("📂 Loading PDF from:", pdf_path)

        loader = PyPDFLoader(pdf_path)


        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"❌ PDF not found: {pdf_path}")

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        # ✅ Split documents
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=80
        )
        docs = splitter.split_documents(documents)

        # ✅ Create embeddings + vector DB
        embedding = OpenAIEmbeddings()
        vectordb = Chroma.from_documents(docs, embedding)

        # ✅ Create retriever
        retriever = vectordb.as_retriever(search_kwargs={"k": 8})

        print("✅ PDF loaded and vector DB ready")

    except Exception as e:
        print("❌ Startup Error:", str(e))
        retriever = None
        llm = None

# 🔹 Main API
@app.post("/ask")
def ask_question(req: QueryRequest):
    global retriever, llm

    try:
        # ✅ Safety checks
        if retriever is None:
            return {"error": "Retriever not initialized. Check PDF loading."}

        if llm is None:
            return {"error": "LLM not initialized. Check API key."}

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

        # ✅ Remove duplicates
        unique_docs = list({doc.page_content: doc for doc in all_docs}.values())

        context = "\n".join([doc.page_content for doc in unique_docs])

        # 🔥 Prompt
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

        # ✅ Sources
        pages = list(set([doc.metadata.get("page", 0) + 1 for doc in unique_docs]))

        return {
            "answer": response.content,
            "sources": sorted(pages)
        }

    except Exception as e:
        return {"error": str(e)}