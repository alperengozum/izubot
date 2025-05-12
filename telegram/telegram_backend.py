import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "7520710251:AAHvm8qWYqv0KLD5uSC_uxA25-HlifBxRIk"
API_URL = "http://127.0.0.1:8000/query"  # Buraya kendi /query endpoint URL’ini koy

logging.basicConfig(level=logging.INFO)

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba! İZÜBOT'a hoş geldin. Sorunu yaz, hemen cevaplayayım.")

# Mesaj geldiğinde çalışır
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question_text = update.message.text

    payload = {
        "question": question_text
        # Eğer fakülte filtresi eklemek istersen: "fakulte": "Mühendislik Fakültesi"
    }

    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            data = response.json()
            mesaj = (
                f"📌 *Soru:* {data['soru']}\n"
                f"✅ *Cevap:* {data['cevap']}\n"
                f"🏛️ *Fakülte:* {data['fakulte']}\n"
                f"📚 *Konu:* {data['konu']}\n"
                f"📊 *Skor:* {data['skor']:.2f}"
            )
        elif response.status_code == 404:
            mesaj = "❌ Üzgünüm, bu soruya uygun bir cevap bulamadım."
        else:
            mesaj = "⚠️ Bir hata oluştu, lütfen daha sonra tekrar dene."

    except Exception as e:
        logging.error(e)
        mesaj = "⛔ Sistemsel bir hata oluştu."

    await update.message.reply_text(mesaj, parse_mode="Markdown")

# Bot uygulaması başlatma
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

print("Telegram bot çalışıyor...")
app.run_polling()
