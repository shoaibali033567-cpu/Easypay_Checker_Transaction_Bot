import os
import re
import requests
from flask import Flask, request, jsonify

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)

def check_transaction(order_id):
    """Check payment status."""
    try:
        response = requests.get(
    "https://easypay-checker-transaction-bot.vercel.app/api/inquire-easypay",
    params={"order_id": order_id},
    timeout=10,
)
        data = response.json()  # parse JSON properly

        status = data.get("transactionStatus", "").upper()
        settlement = data.get("settlementStatus", "").upper()
        desc = data.get("responseDesc", "").upper()

        if status == "PAID" and settlement == "SETTLED":
            return "✅ Transaction paid and already settled."
        elif status == "FAILED":
            return "❌ Transaction failed, I’ll let you know when it’s settled."
        elif desc == "SUCCESS":
            return "✅ Transaction successful and processed."
        else:
            return "ℹ️ Couldn’t determine the status. Please check the order ID again."
    except Exception as e:
        return f"⚠️ Error checking transaction: {e}"

@app.route("/api/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()

        if not chat_id:
            return jsonify({"ok": True})  # nothing to do

        if re.match(r"^[A-Za-z0-9]+$", text):

            requests.post(f"{TELEGRAM_API}/sendMessage",
                          json={"chat_id": chat_id, "text": "Okay, checking..."})
            result = check_transaction(text)
            requests.post(f"{TELEGRAM_API}/sendMessage",
                          json={"chat_id": chat_id, "text": result})
        else:
            requests.post(f"{TELEGRAM_API}/sendMessage",
                          json={"chat_id": chat_id, "text": "Please send your order ID (numbers only)."})

        return jsonify({"ok": True})
    except Exception as e:
        print("Webhook error:", e)
        return jsonify({"error": str(e)}), 500
