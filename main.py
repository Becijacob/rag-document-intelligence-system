import os
import shutil
from typing import List

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

class QueryRequest(BaseModel):
    question: str

# ✅ Root
@app.get("/")
def home():
    return {"message": "Multi-PDF RAG API running"}

# ✅ Upload MULTIPLE PDFs
@app.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    global vectordb, retriever, llm

    try:
        all_docs = []

        for file in files:
            file_path = f"/tmp/{file.filename}"

            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Load PDF
            loader = PyPDFLoader(file_path)
            documents = loader.load()

            # Add metadata (important)
            for doc in documents:
                doc.metadata["source"] = file.filename

            all_docs.extend(documents)

        # Split
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=80
        )
        docs = splitter.split_documents(all_docs)

        # Embeddings + DB
        embedding = OpenAIEmbeddings()
        vectordb = Chroma.from_documents(docs, embedding)

        retriever = vectordb.as_retriever(search_kwargs={"k": 10})

        # LLM
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY missing")

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        return {"message": f"{len(files)} PDFs uploaded successfully"}

    except Exception as e:
        return {"error": str(e)}

# ✅ Ask
@app.post("/ask")
def ask_question(req: QueryRequest):
    global retriever, llm

    try:
        if retriever is None:
            return {"error": "Upload PDFs first"}

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

        sources = list(set([doc.metadata.get("source", "Unknown") for doc in docs]))
        pages = list(set([doc.metadata.get("page", 0) + 1 for doc in docs]))

        return {
            "answer": response.content,
            "sources": sources,
            "pages": sorted(pages)
        }

    except Exception as e:
        return {"error": str(e)}