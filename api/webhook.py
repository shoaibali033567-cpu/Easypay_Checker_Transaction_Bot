import os
from telegram import Update
from telegram.ext import Application, ApplicationBuilder
from telegram.ext import MessageHandler, filters, ContextTypes
import requests
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

async def check_transaction(order_id):
    try:
        response = requests.get("https://naspropvt.vercel.app/inquire-easypay", params={"order_id": order_id})
        data = response.text.lower()
        if "paid" in data and "settled" in data:
            return "✅ Transaction paid and already settled."
        elif "failed" in data:
            return "❌ Transaction failed. I’ll let you know when it’s settled."
        else:
            return "ℹ️ Couldn’t determine the status. Please check the order ID again."
    except Exception as e:
        return f"⚠️ Error checking transaction: {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.isdigit():
        await update.message.reply_text("Okay, checking...")
        result = await check_transaction(text)
        await update.message.reply_text(result)

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route("/api/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

def handler(event, context):
    return app(event, context)
