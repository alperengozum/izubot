from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack import Document

document_store = FAISSDocumentStore(embedding_dim=768, faiss_index_factory_str="Flat")

retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="dbmdz/bert-base-turkish-cased",
    model_format="transformers"
)

docs = [
    Document(content="İslami finans, faizsiz finans prensiplerine dayanır.",
             meta={"question": "İslami finans nedir?", "fakulte": "İİBF"}),
    Document(content="Burs başvuruları öğrenci işleri sayfasından yapılır.",
             meta={"question": "Burs başvurusu nasıl yapılır?", "fakulte": "Genel"})
]

document_store.write_documents(docs)

document_store.update_embeddings(retriever)

while True:
    query = input("Soru: ")
    results = retriever.retrieve(query=query, top_k=1)
    print("\nCevap:", results[0].content)
    print("Fakülte:", results[0].meta["fakulte"])
    print("-" * 50)
