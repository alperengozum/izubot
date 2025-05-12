from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack import Document
import pandas as pd
import pickle
from difflib import SequenceMatcher
import os

# 🔹 GEREKSİZ FAISS DOSYALARINI TEMİZLE
for fname in ["faiss_index.faiss", "faiss_index.json", "faiss_document_store.db"]:
    if os.path.exists(fname):
        os.remove(fname)

# 🔹 Benzerlik hesaplama fonksiyonu
def get_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# 🔹 Fakülte sınıflandırma modelini yükle
with open("faculty_classifier.pkl", "rb") as f:
    faculty_classifier = pickle.load(f)

# 🔸 FastAPI başlat
app = FastAPI()

# 🔸 CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔸 API veri modeli
class Query(BaseModel):
    question: str
    fakulte: str = None

# 🔹 Excel verisini oku ve temizle
df = pd.read_excel("IzuBot.xlsx")
df_clean = df.dropna(subset=["Soru", "Cevap"]).copy()

# 🔹 Belgeleri oluştur
documents = []
for _, row in df_clean.iterrows():
    doc = Document(
        content=row["Cevap"],
        meta={
            "soru": row["Soru"],
            "fakulte": row["Fakülte"] if pd.notna(row["Fakülte"]) else None,
            "konu": row["Konu Başlığı"] if pd.notna(row["Konu Başlığı"]) else None
        }
    )
    documents.append(doc)

# 🔹 InMemory Document Store (embedding_dim retriever ile uyumlu)
document_store = InMemoryDocumentStore(embedding_dim=768)

# 🔹 Retriever (çok dilli güçlü model)
retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="sentence-transformers/xlm-r-bert-base-nli-stsb-mean-tokens",
    model_format="sentence_transformers"
)

# Belgeleri kaydet ve embed et
document_store.write_documents(documents)
document_store.update_embeddings(retriever)

# 🔹 Ana API endpoint
@app.post("/query")
def query_answer(query: Query):
    try:
        predicted_faculty = query.fakulte or faculty_classifier.predict([query.question])[0]

        retrieved_docs = retriever.retrieve(
            query=query.question,
            top_k=10,
            filters={"fakulte": [predicted_faculty]}
        )

        if not retrieved_docs:
            return {
                "soru": query.question,
                "cevap": "❌ Hiçbir belge bulunamadı.",
                "eşleşen_dataset_sorusu": "—",
                "benzerlik_skoru": 0.0,
                "uyarı": "🔍 Veri kümesinde bu soruya benzer bir içerik yok."
            }

        best_doc = max(retrieved_docs, key=lambda d: get_similarity(query.question, d.meta.get("soru", "")))
        matched_score = get_similarity(query.question, best_doc.meta.get("soru", ""))

        if matched_score < 0.35:
            return {
                "soru": query.question,
                "cevap": "❌ Bu soruya benzer içerik veri kümesinde bulunamadı.",
                "eşleşen_dataset_sorusu": "—",
                "benzerlik_skoru": round(matched_score, 3),
                "uyarı": "⚠️ Soru çok farklı. Lütfen daha açık veya alternatif biçimde sorun."
            }

        response = {
            "soru": query.question,
            "tahmin_edilen_fakulte": predicted_faculty,
            "cevap": best_doc.content,
            "benzerlik_skoru": round(matched_score, 3),
            "eşleşen_dataset_sorusu": best_doc.meta.get("soru", "")
        }

        if matched_score < 0.6:
            response["uyarı"] = "⚠️ Bu cevap düşük eşleşmeyle döndürüldü. Tam doğru olmayabilir."
        elif matched_score < 0.75:
            response["uyarı"] = "ℹ️ Bu cevap kısmen eşleşen bir içerikten döndürüldü."

        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "error": "🚨 Sunucu tarafında bir hata oluştu.",
            "detay": str(e)
        }
