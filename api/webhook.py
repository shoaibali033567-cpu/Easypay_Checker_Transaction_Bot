import os
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Create a Flask app
app = Flask(__name__)

# Telegram bot application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# --- Logic to check transaction ---
async def check_transaction(order_id):
    try:
        response = requests.get(
            "https://naspropvt.vercel.app/inquire-easypay",
            params={"order_id": order_id},
            timeout=10
        )
        data = response.text.lower()
        if "paid" in data and "settled" in data:
            return "✅ Transaction paid and already settled."
        elif "failed" in data:
            return "❌ Transaction failed, I’ll let you know when it’s settled."
        else:
            return "ℹ️ Couldn’t determine the status. Please check the order ID again."
    except Exception as e:
        return f"⚠️ Error checking transaction: {e}"

# --- Handler for text messages ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.isdigit():
        await update.message.reply_text("Okay, checking...")
        result = await check_transaction(text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Please send your order ID (numbers only).")

# Add message handler
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Webhook route ---
@app.route("/api/webhook", methods=["POST"])
def webhook():
    """Receive updates from Telegram"""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
        return "ok", 200
    except Exception as e:
        print("Webhook error:", e)
        return str(e), 500
