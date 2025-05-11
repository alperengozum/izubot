from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack import Document

# 1. FAISS store (boş başlatılır)
document_store = FAISSDocumentStore(embedding_dim=768, faiss_index_factory_str="Flat")

# 2. Retriever daha önce oluşturulmalı
retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="dbmdz/bert-base-turkish-cased",
    model_format="transformers"
)

# 3. Mini belge listesi
docs = [
    Document(content="İslami finans, faizsiz finans prensiplerine dayanır.",
             meta={"question": "İslami finans nedir?", "fakulte": "İİBF"}),
    Document(content="Burs başvuruları öğrenci işleri sayfasından yapılır.",
             meta={"question": "Burs başvurusu nasıl yapılır?", "fakulte": "Genel"})
]

# 4. Belgeleri retriever ile birlikte ekle
document_store.write_documents(docs)

# 5. Embedding'leri oluştur (bu sefer FAISS eşleşir)
document_store.update_embeddings(retriever)

# 6. Soru sor
while True:
    query = input("Soru: ")
    results = retriever.retrieve(query=query, top_k=1)
    print("\nCevap:", results[0].content)
    print("Fakülte:", results[0].meta["fakulte"])
    print("-" * 50)
