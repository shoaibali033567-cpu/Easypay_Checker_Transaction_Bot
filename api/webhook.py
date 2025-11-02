import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me your EasyPay Order ID and I’ll check its status.")

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
        await update.message.reply_text("🔎 Checking your transaction...")
        result = await check_transaction(text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("❓ Please send a valid numeric order ID.")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def handler(event, context):
    try:
        return await app.run_webhook(event, context)
    except Exception as e:
        print("⚠️ Error:", e)
        return {"statusCode": 500, "body": str(e)}
