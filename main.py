import os
import shutil
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Globals
vectordb = None
retriever = None
llm = None

UPLOAD_PATH = "uploaded.pdf"

class QueryRequest(BaseModel):
    question: str

# ✅ Root
@app.get("/")
def home():
    return {"message": "RAG API running"}

# ✅ Upload PDF
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global vectordb, retriever, llm

    try:
        # Save file
        with open(UPLOAD_PATH, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load PDF
        loader = PyPDFLoader(UPLOAD_PATH)
        documents = loader.load()

        # Split
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=80
        )
        docs = splitter.split_documents(documents)

        # Create embeddings
        embedding = OpenAIEmbeddings()
        vectordb = Chroma.from_documents(docs, embedding)

        retriever = vectordb.as_retriever(search_kwargs={"k": 10})

        # Initialize LLM
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("API key missing")

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        return {"message": "PDF uploaded and processed"}

    except Exception as e:
        return {"error": str(e)}

# ✅ Ask question
@app.post("/ask")
def ask_question(req: QueryRequest):
    global retriever, llm

    try:
        if retriever is None:
            return {"error": "Upload a PDF first"}

        if llm is None:
            return {"error": "LLM not initialized"}

        docs = retriever.invoke(req.question)

        context = "\n".join([doc.page_content for doc in docs])

        prompt = f"""
You are an AI assistant.

Answer ONLY using the context.
If answer not found, say "I don't know".

Context:
{context}

Question:
{req.question}
"""

        response = llm.invoke(prompt)

        pages = list(set([doc.metadata.get("page", 0) + 1 for doc in docs]))

        return {
            "answer": response.content,
            "sources": sorted(pages)
        }

    except Exception as e:
        return {"error": str(e)}