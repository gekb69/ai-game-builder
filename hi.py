
# telegram_bot.py
# Simple Telegram bot that forwards commands to an n8n webhook.
# Uses python-telegram-bot (v13/v20 compatible pseudocode). Install: pip install python-telegram-bot requests
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

N8N_WEBHOOK = "https://your-n8n.example/webhook/telegram-webhook"
BOT_TOKEN = "REPLACE_WITH_YOUR_TELEGRAM_BOT_TOKEN"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً! أرسل الأمر باستخدام /new <مهمة>")

async def new_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_text = ' '.join(context.args)
    if not task_text:
        await update.message.reply_text("اكتب المهمة بعد الأمر، مثلاً: /new Implement player movement save system in Unity")
        return
    payload = {
        "text": task_text,
        "user_id": update.effective_user.id,
        "chat_id": update.effective_chat.id
    }
    try:
        r = requests.post(N8N_WEBHOOK, json=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        job_id = data.get("id", "unknown")
        await update.message.reply_text(f"تم إنشاء المهمة. JobID: {job_id}\nسأعلمك بالنتائج.")
    except Exception as e:
        logger.exception("Failed to call n8n webhook")
        await update.message.reply_text(f"حدث خطأ: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # For future use: handle approve/reject inline buttons
    await query.edit_message_text(text=f"Selected option: {query.data}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_task))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot started. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == '__main__':
    main()