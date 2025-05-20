import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Telegram Bot Token'ı
BOT_TOKEN = "7777415624:AAFhLvq3P4e-ZfZYbrNShEBHWMRdvZBicQ0"  # Lütfen buraya kendi bot token'ını yaz

# FastAPI (OpenPipe destekli) backend URL
API_URL = "http://127.0.0.1:8000/query"

# Loglama
logging.basicConfig(level=logging.INFO)

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Merhaba! Chat With Izu'ya hoş geldin. Sorunu yaz, hemen cevaplayayım.")

# Mesajları yakalayıp OpenPipe'a yönlendiren handler
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question_text = update.message.text
    payload = {"question": question_text}

    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            data = response.json()
            mesaj = f"✅ *Cevap:* {data['cevap']}"
        else:
            mesaj = "⚠️ Bir hata oluştu, lütfen daha sonra tekrar dene."

    except Exception as e:
        logging.error(e)
        mesaj = "⛔ Sistemsel bir hata oluştu."

    await update.message.reply_text(mesaj, parse_mode="Markdown")

# Botu başlat
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

print("🤖 Telegram bot çalışıyor...")
app.run_polling()
