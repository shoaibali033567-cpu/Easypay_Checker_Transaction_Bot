import os
import asyncio
import requests
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Flask server
app = Flask(__name__)

# Create PTB application (but do NOT call run_polling)
application = Application.builder().token(BOT_TOKEN).build()


async def check_transaction(order_id: str) -> str:
    """Check payment status."""
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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    text = update.message.text.strip()
    if text.isdigit():
        await update.message.reply_text("Okay, checking...")
        result = await check_transaction(text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Please send your order ID (numbers only).")


# Add handler
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


@app.route("/api/webhook", methods=["POST"])
def webhook():
    """Handle incoming webhook requests from Telegram."""
    try:
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)

        # Run PTB update processing asynchronously
        asyncio.run(application.process_update(update))

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print("Webhook error:", e)
        return jsonify({"error": str(e)}), 500
