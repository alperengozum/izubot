from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openpipe import OpenAI
import os



# OpenPipe istemcisini başlat
client = OpenAI(
    openpipe={"api_key": "opk_90dda99a1d3a41c12221c979b282d4f38b2a065fe0"}
)

# FastAPI uygulaması
app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API veri modeli
class Query(BaseModel):
    question: str

# Ana API endpoint
@app.post("/query")
def query_answer(query: Query):
    try:
        # OpenPipe model sorgusu
        completion = client.chat.completions.create(
            model="openpipe:purple-days-stick",  # Buraya kendi model ID'ni yaz
            messages=[
                {
                    "role": "user",
                    "content": query.question
                }
            ],
            temperature=0,
            openpipe={
                "tags": {
                    "prompt_id": "chatbot-query"
                }
            },
        )

        answer = completion.choices[0].message.content

        return {
            "soru": query.question,
            "cevap": answer
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "error": "🚨 Sunucu tarafında bir hata oluştu.",
            "detay": str(e)
        }
