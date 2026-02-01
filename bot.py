import os, time, yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

# --- কনফিগারেশন ---
API_ID = 34850757
API_HASH = "f35b510c4b5b28851b715f349eb9a4d9"
BOT_TOKEN = "8373972531:AAEbOKuzUbF2e-qcWEhwqoPz4qEcj-nXiEM"

DEV_NAME = "Apu Jeet"
DEV_FB = "https://www.facebook.com/share/1DLXmXHthS/"
DEV_PHOTO = "https://e.top4top.io/p_3684vhzt74.jpg" 

app = Client("pro_downloader_final", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 📊 ডাউনলোড প্রগ্রেস বার ফাংশন
def progress(current, total, message, start_time):
    now = time.time()
    diff = now - start_time
    if round(diff % 3) == 0 or current == total:
        percent = current * 100 / total
        speed = current / diff if diff > 0 else 0
        text = f"📊 **ডাউনলোড হচ্ছে:** {percent:.1f}%\n⚡ **স্পিড:** {speed/1024:.1f} KB/s"
        try: message.edit(text)
        except: pass

@app.on_message(filters.command("start") | filters.group)
def start(client, message):
    text = (f"🚀 **{DEV_NAME} প্রিমিয়াম ডাউনলোডার**\n\n"
            "✅ YouTube, FB, TikTok সাপোর্ট\n"
            "✅ থাম্বনেইল প্রিভিউ ও প্রগ্রেস বার\n"
            "✅ অডিও (MP3) কনভার্টার\n"
            "✅ **Copyright-Safe Mode** (মেটাডেটা ক্লিনার)")
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 ডেভেলপার ফেসবুক", url=DEV_FB)],
        [InlineKeyboardButton("📥 ডাউনলোড শুরু করুন", callback_data="ask_link")]
    ])
    try: message.reply_photo(photo=DEV_PHOTO, caption=text, reply_markup=buttons)
    except: message.reply_text(text, reply_markup=buttons)

@app.on_callback_query(filters.regex("ask_link"))
def ask_link(client, callback_query):
    callback_query.message.reply_text("🔗 **আপনার লিঙ্কটি এখানে পাঠান:**", reply_markup=ForceReply(selective=True))

@app.on_message(filters.text & filters.regex(r'http'))
def handle_link(client, message):
    url = message.text
    status = message.reply_text("🔍 **লিঙ্ক চেক করা হচ্ছে...**", quote=True)
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            thumb = info.get('thumbnail')
            title = info.get('title', 'Media')[:50]
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 720p", callback_data=f"dl|720|{url}"),
                 InlineKeyboardButton("🎬 360p", callback_data=f"dl|360|{url}")],
                [InlineKeyboardButton("🎵 MP3 Audio", callback_data=f"dl|mp3|{url}"),
                 InlineKeyboardButton("🖼️ Thumbnail", callback_data=f"dl|photo|{url}")]
            ])
            message.reply_photo(photo=thumb, caption=f"📝 **টাইটেল:** `{title}`\n\n📥 **কোয়ালিটি সিলেক্ট করুন:**", reply_markup=buttons)
            status.delete()
    except: status.edit("❌ লিঙ্কটি সাপোর্ট করছে না।")

@app.on_callback_query(filters.regex(r'^dl\|'))
def download_handler(client, callback_query):
    _, q, url = callback_query.data.split("|")
    status = callback_query.message.edit(f"⚙️ **{q} প্রসেস শুরু হচ্ছে...**")
    file_name = f"file_{int(time.time())}.mp4" if q != "mp3" else f"file_{int(time.time())}.mp3"

    if q == "photo":
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                callback_query.message.reply_photo(photo=info.get('thumbnail'), caption=f"✅ থাম্বনেইল ডাউনলোড সম্পন্ন!\n👤 {DEV_NAME}")
                return status.delete()
        except: return status.edit("❌ ছবি পাওয়া যায়নি!")

    # 🚫 Copyright-Safe Mode (মেটাডেটা ক্লিনার যুক্ত)
    ydl_opts = {
        'format': f'bestvideo[height<={q}]+bestaudio/best' if q.isdigit() else 'bestaudio/best',
        'outtmpl': file_name,
        'postprocessors': [{'key': 'FFmpegMetadata', 'add_metadata': False}]
    }
    
    if q == "mp3":
        ydl_opts['postprocessors'].append({'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        status.edit("📤 **টেলিগ্রামে পাঠানো হচ্ছে...**")
        start_t = time.time()
        
        if q == "mp3": client.send_audio(callback_query.message.chat.id, audio=file_name, caption=f"🎵 {DEV_NAME}", progress=progress, progress_args=(status, start_t))
        else: client.send_video(callback_query.message.chat.id, video=file_name, caption=f"✅ {q}p সম্পন্ন!", progress=progress, progress_args=(status, start_t))
        
        status.delete()
    except: status.edit("❌ ডাউনলোড ব্যর্থ! সার্ভারে FFmpeg সমস্যা হতে পারে।")
    finally:
        if os.path.exists(file_name): os.remove(file_name)

app.run()
