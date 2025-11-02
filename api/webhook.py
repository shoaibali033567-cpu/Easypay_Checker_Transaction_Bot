import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# Telegram bot token (store in Vercel environment variable)
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def check_transaction(order_id):
    try:
        response = requests.get("https://naspropvt.vercel.app/inquire-easypay", params={"order_id": order_id})
        data = response.text.lower()

        if "paid" in data and "settled" in data:
            return "✅ Transaction paid and already settled."
        elif "failed" in data:
            return "❌ Transaction failed, I'll let you know when it’s settled. Thank you."
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

# Create application
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# This is the Vercel handler
async def handler(event, context):
    return await app.run_webhook(event, context)
