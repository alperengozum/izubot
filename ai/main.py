from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack import Document
import pandas as pd
import os

# 🔸 FastAPI uygulamasını başlat
app = FastAPI()

# 🔸 API veri modeli
class Query(BaseModel):
    question: str
    fakulte: str = None  # opsiyonel

    from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # sadece frontend'e izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 🔹 FAISS dosyalarını temizle (geliştirme için)
for fname in ["faiss_index.faiss", "faiss_index.json", "faiss_document_store.db"]:
    if os.path.exists(fname):
        os.remove(fname)

# 🔹 Excel dosyasını yükle
df = pd.read_excel("IzuBot.xlsx")
df_clean = df.dropna(subset=["Soru", "Cevap"]).copy()

# 🔹 Belgeleri oluştur
documents = []
for _, row in df_clean.iterrows():
    text = f"Soru: {row['Soru']}\nCevap: {row['Cevap']}"
    meta = {
        "fakulte": row["Fakülte"] if pd.notna(row["Fakülte"]) else None,
        "konu": row["Konu Başlığı"] if pd.notna(row["Konu Başlığı"]) else None
    }
    documents.append(Document(content=text, meta=meta))

# 🔹 FAISS bellek deposu
document_store = FAISSDocumentStore(embedding_dim=384, faiss_index_factory_str="Flat")

# 🔹 Embedding Retriever (MiniLM çok dilli)
retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_format="sentence_transformers"
)

# 🔹 Belgeleri yaz ve embed’le
document_store.write_documents(documents)
document_store.update_embeddings(retriever)

# 🔹 API endpoint: /query
@app.post("/query")
def query_answer(query: Query):
    filters = {}

    if query.fakulte:
        filters["fakulte"] = [query.fakulte]

    results = retriever.retrieve(query=query.question, top_k=3, filters=filters if filters else None)

    if not results:
        raise HTTPException(status_code=404, detail="❌ Uygun bir cevap bulunamadı.")

    top_doc = results[0]
    return {
        "soru": query.question,
        "cevap": top_doc.content,
        "fakulte": top_doc.meta.get("fakulte"),
        "konu": top_doc.meta.get("konu"),
        "skor": round(top_doc.score, 3)
    }
