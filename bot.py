import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Replace with your own Telegram Bot token
BOT_TOKEN = "8560028243:AAEbCOnnCQnIEvAwWhoJHT2BAtKpRv3SEZ0"

async def check_transaction(order_id):
    try:
        # Requesting the transaction status from the URL you provided
        response = requests.get("https://naspropvt.vercel.app/inquire-easypay", params={"order_id": order_id})
        data = response.text.lower()

        # Checking if the transaction is paid and settled
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
    if text.isdigit():  # if user sends a number (order id)
        await update.message.reply_text("Okay, checking...")
        result = await check_transaction(text)
        await update.message.reply_text(result)

# Build the application with the token
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Handle incoming messages
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Start the bot
app.run_polling()
