from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv()  

import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "secrettoken")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "EAAT1KSnc054BO5qksMupmHc6keDCVyYAEJ0kIVOX3jgqonzA8SEFmUcQYZCLffJIA5kF68TZCfEFdTmEC3wXZAFnnzdfcK7BZBprqUgQ2s0fkfkyfhqBNqH7MyOsiEmGiAoGWFlqATAZAKBrlkmJjsmO53kJPBo4vQbscFdkGbujoubeCpQEUDMqzjY8RCcfdcixuSAGp7EG2a9Dqv5HSdadMVccUt3bBxFoZD")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "692885273889590")

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
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

        query_response = requests.post(
            "http://localhost:8000/query",  # senin API endpointin
            json={"question": user_message}
        )

        if query_response.status_code == 200:
            answer = query_response.json()["cevap"]
        else:
            answer = "❌ Üzgünüm, uygun bir cevap bulamadım."

        send_message(sender, answer)
    except Exception as e:
        print(f"❗ Hata: {e}")
    return "OK", 200

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

if __name__ == "__main__":
    app.run(port=3001)
