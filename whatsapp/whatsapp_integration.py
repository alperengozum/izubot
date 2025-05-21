from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


VERIFY_TOKEN = "secrettoken"
ACCESS_TOKEN = "EAAT1KSnc054BO3IeZBSHjTYm8tX2ZCHF6FYU7ZC7cPnR2VIgNeolkZAQmwQUfh2OtwqwtNQisfZCV8SuZAnelr8fBf95XWP1pZAKkm0Hxxd5sZBlmlHBYOct7mlgYuFmEoo3XL4ZCiLZBOtSoeIq2P7tVHfweWa3W7c5AFpaGpZAwYAgApCwfVrxIwKQpgK2qIHb0JFBwzUMyGPl4OLXB6sukVFcd90NDr27SPXZAzoZD"
PHONE_NUMBER_ID = "692885273889590"

# 🧠 OpenPipe destekli backend API adresi
API_URL = "http://localhost:8000/query"


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        entry = data['entry'][0]
        message = entry['changes'][0]['value']['messages'][0]
        sender = message['from']
        user_message = message['text']['body']

        
        query_response = requests.post(API_URL, json={"question": user_message})

        if query_response.status_code == 200:
            cevap = query_response.json().get("cevap", "Cevap alınamadı.")
        else:
            cevap = "❌ Üzgünüm, bir hata oluştu."

        
        send_message(sender, cevap)

    except Exception as e:
        print(f"❗ Hata oluştu: {e}")

    return "OK", 200

# WhatsApp yanıt gönderici
def send_message(recipient, message):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {
            "body": message
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Uygulamayı başlat
if __name__ == "__main__":
    app.run(port=3001)
