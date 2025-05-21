import os
import yt_dlp
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /download <playlist_url> to get MP3s.")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /download <playlist_url>")
        return
    url = context.args[0]

    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/%(title)s.%(ext)s"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'playlistend': 1,  # limit to 1 video for free tier
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    await update.message.reply_text("Downloading and converting to MP3...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir(output_dir):
            if file.endswith(".mp3"):
                with open(os.path.join(output_dir, file), "rb") as audio:
                    await update.message.reply_audio(audio)
        await update.message.reply_text("Done!")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("download", download))

@app.route("/", methods=["GET"])
def index():
    return "Bot is alive."

if __name__ == "__main__":
    bot_app.run_polling()
