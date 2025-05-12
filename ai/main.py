from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from haystack.document_stores import InMemoryDocumentStore, FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack import Document
import pandas as pd
import pickle
from difflib import SequenceMatcher
import os

app = FastAPI()

class Query(BaseModel):
    question: str
    fakulte: str = None  # opsiyonel

    from fastapi.middleware.cors import CORSMiddleware

# 🔹 Benzerlik hesaplama fonksiyonu
def get_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# 🔹 Fakülte sınıflandırma modelini yükle
with open("faculty_classifier.pkl", "rb") as f:
    faculty_classifier = pickle.load(f)

# 🔸 FastAPI başlat
app = FastAPI()

# 🔸 CORS ayarları (frontend için)
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
for fname in ["faiss_index.faiss", "faiss_index.json", "faiss_document_store.db"]:
    if os.path.exists(fname):
        os.remove(fname)

df = pd.read_excel("IzuBot.xlsx")
df_clean = df.dropna(subset=["Soru", "Cevap"]).copy()

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

# 🔹 Document Store
document_store = InMemoryDocumentStore(embedding_dim=768)

# 🔹 Retriever (güçlü çok dilli model)
document_store = FAISSDocumentStore(embedding_dim=384, faiss_index_factory_str="Flat")

retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="sentence-transformers/xlm-r-bert-base-nli-stsb-mean-tokens",
    model_format="sentence_transformers"
)

document_store.write_documents(documents)
document_store.update_embeddings(retriever)

# 🔹 API endpoint
@app.post("/query")
def query_answer(query: Query):
    try:
        predicted_faculty = query.fakulte or faculty_classifier.predict([query.question])[0]

        retrieved_docs = retriever.retrieve(
            query=query.question,
            top_k=7,
            filters={"fakulte": [predicted_faculty]}
        )

        if not retrieved_docs:
            return {
                "soru": query.question,
                "cevap": "❌ Hiçbir belge bulunamadı.",
                "eşleşen_dataset_sorusu": "—",
                "benzerlik_skoru": 0.0,
                "uyarı": "🔍 Soru veri setinde benzer içerik içermiyor olabilir."
            }

        # En uygun belgeyi bul ve eşleşme skorunu hesapla
        best_doc = max(retrieved_docs, key=lambda d: get_similarity(query.question, d.meta.get("soru", "")))
        matched_score = get_similarity(query.question, best_doc.meta.get("soru", ""))

        # Çok düşük eşleşmeler için hiç cevap verme
        if matched_score < 0.35:
            return {
                "soru": query.question,
                "cevap": "❌ Bu soruya benzer içerik veri kümesinde bulunamadı.",
                "eşleşen_dataset_sorusu": "—",
                "benzerlik_skoru": round(matched_score, 3),
                "uyarı": "⚠️ Soru çok farklı. Daha açık yazın veya yeniden deneyin."
            }

        # Temel cevap
        response = {
            "soru": query.question,
            "tahmin_edilen_fakulte": predicted_faculty,
            "cevap": best_doc.content,
            "benzerlik_skoru": round(matched_score, 3),
            "eşleşen_dataset_sorusu": best_doc.meta.get("soru", "")
        }

        # Orta düzey eşleşmelere uyarı ekle
        if matched_score < 0.45:
            response["uyarı"] = "⚠️ Bu cevap düşük eşleşmeye göre döndürüldü. Tam doğru olmayabilir."
        elif matched_score < 0.75:
            response["uyarı"] = "ℹ️ Bu cevap kısmen eşleşen içerikten döndürüldü."

        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "error": "🚨 Sunucu tarafında bir hata oluştu.",
            "detay": str(e)
        }
