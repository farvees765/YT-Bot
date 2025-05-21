import os
import yt_dlp
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /download <playlist_url> to download MP3.")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /download <playlist_url>")
        return
    url = context.args[0]

    os.makedirs("downloads", exist_ok=True)
    output_path = "downloads/%(title)s.%(ext)s"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'playlistend': 1,  # Download 1 video
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    await update.message.reply_text("Downloading...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("downloads"):
            if file.endswith(".mp3"):
                with open(os.path.join("downloads", file), "rb") as audio:
                    await update.message.reply_audio(audio)
        await update.message.reply_text("Done!")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    Thread(target=run_web).start()
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("download", download))
    app_bot.run_polling()

if __name__ == "__main__":
    main()
