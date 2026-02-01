import telebot
import yt_dlp
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8224183581:AAE9yGtRhaT8zsIr3v0Gc5WK1PrvHsadliw"
bot = telebot.TeleBot(TOKEN)

user_links = {}

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(
        msg,
        "👋 Welcome!\n\n"
        "📥 YouTube / Facebook / TikTok লিংক পাঠাও\n"
        "🎚 Quality সিলেক্ট করে ডাউনলোড করো\n\n"
        "⚠️ Personal use only"
    )

# ---------- MP3 COMMAND ----------
@bot.message_handler(commands=['mp3'])
def mp3_cmd(msg):
    bot.reply_to(
        msg,
        "🎵 MP3 পেতে ভিডিও লিংক পাঠাও\nতারপর 🎵 MP3 বাটনে চাপো"
    )

# ---------- LINK HANDLER ----------
@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def link_handler(msg):
    chat_id = msg.chat.id
    url = msg.text.strip()

    bot.send_message(chat_id, "🔍 ভিডিও তথ্য আনা হচ্ছে...")

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)

        # ---------- COPYRIGHT SAFE ----------
        if info.get("duration", 0) > 600:
            bot.send_message(chat_id, "❌ ১০ মিনিটের বেশি ভিডিও অনুমোদিত নয়")
            return

        user_links[chat_id] = url

        caption = (
            f"🎬 {info.get('title')}\n"
            f"📺 {info.get('uploader')}\n"
            f"⏱ {int(info.get('duration', 0)//60)} min\n\n"
            "👇 Quality বেছে নাও"
        )

        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("🎬 360p", callback_data="360"),
            InlineKeyboardButton("🎥 720p", callback_data="720")
        )
        keyboard.row(
            InlineKeyboardButton("🎵 MP3", callback_data="mp3")
        )

        bot.send_photo(
            chat_id,
            info.get("thumbnail"),
            caption=caption,
            reply_markup=keyboard
        )

    except Exception:
        bot.send_message(chat_id, "❌ লিংক সাপোর্টেড না বা Private ভিডিও")

# ---------- BUTTON HANDLER ----------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    quality = call.data
    url = user_links.get(chat_id)

    bot.edit_message_caption(
        "⬇️ Download শুরু হচ্ছে...",
        chat_id,
        call.message.message_id
    )

    try:
        if quality == "mp3":
            ydl_opts = {
                'format': 'bestaudio',
                'outtmpl': 'audio.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }]
            }
        else:
            ydl_opts = {
                'format': f'bestvideo[height<={quality}]+bestaudio/best',
                'outtmpl': 'video.%(ext)s'
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir():
            if file.startswith("video") or file.startswith("audio"):
                with open(file, 'rb') as f:
                    if quality == "mp3":
                        bot.send_audio(
                            chat_id,
                            f,
                            caption="🎵 MP3 Audio\n⚠️ Personal use only"
                        )
                    else:
                        bot.send_video(
                            chat_id,
                            f,
                            caption="🎬 Video\n⚠️ Personal use only"
                        )
                os.remove(file)

    except Exception:
        bot.send_message(chat_id, "❌ ডাউনলোড ব্যর্থ!")

# ---------- RUN ----------
bot.polling(non_stop=True)
