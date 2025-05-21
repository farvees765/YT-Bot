import os
import yt_dlp
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /download <playlist_url> to get started!")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /download <playlist_url>")
        return
    url = context.args[0]

    output_path = "downloads/%(title)s.%(ext)s"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'playlistend': 3  # Limit for testing
    }

    await update.message.reply_text("Downloading playlist...")

    try:
        os.makedirs("downloads", exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await update.message.reply_text("Download complete.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("download", download))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put(update)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

if __name__ == "__main__":
    bot_app.run_polling()
