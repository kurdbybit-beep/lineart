import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp

# --- پێزانینێن بوتێ ---
TOKEN = "8933985744:AAETq8QY3O1RkvHYJSz_Gx27cKWKBfvB29I"
CHANNEL_URL = "https://t.me/tech_ai_falah"
CHANNEL_ID = "@tech_ai_falah" 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# فەنکشنا پشکنینا جوین بوونێ
async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# فەرمانا /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    
    keyboard = [
        [InlineKeyboardButton("Channel 📢", url=CHANNEL_URL)],
        [InlineKeyboardButton("من جوین کر ✅", callback_data='check_sub')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"تو خێرهاتی {user_name}، پێدویستە ل دەستپێکێ کەناڵێ مە جوین ببی دا بشێی هەر ڤیدیۆیەکا تە ڤێت داونلود بکەی.\n\n"
        "بۆ ڤیدیۆیێن: YouTube, TikTok, Instagram, Facebook, Pinterest, Twitter(X), Snapchat",
        reply_markup=reply_markup
    )

# پشکنینا دوگمێ "من جوین کر"
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    if await is_subscribed(user_id, context):
        await query.edit_message_text(
            "تو سەرکەفتی! 🎉\n\nهر ڤیدیۆیەکا تە هەبیت لینکی فڕێکە، پەیجێ Tech Ai دێ بۆ تە داونلود کەت."
        )
    else:
        await query.message.reply_text("تۆ هێشتا نەبوویە ئەندام! تکایە سەرەتا جوین بکە پاشان کلیک ل 'من جوین کر' بکە.")

# فەنکشنا داونلودێ (بۆ هەمی سایتان)
async def download_video(url, user_id):
    output_filename = f"video_{user_id}.mp4"
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_filename,
        'quiet': True,
        'no_warnings': True,
        # زێدەکرنا User-Agent دا کو سایت بوتێ بلۆک نەکەن
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_filename
    except Exception as e:
        logging.error(f"Error downloading: {e}")
        return None

# وەرگرتنا لینکان
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = update.message.text
    
    if not url.startswith("http"): return

    if not await is_subscribed(user_id, context):
        await update.message.reply_text(f"ببورە، پێدویستە سەرەتا د کەناڵێ مە دا جوین ببی:\n{CHANNEL_URL}")
        return

    status_msg = await update.message.reply_text("خەریکە ڤیدیۆیێ ئامادە دکەم... ⏳")
    
    # بکارئینانا loop.run_in_executor دا کو بوت بلۆک نەبیت دەمێ داونلودێ
    loop = asyncio.get_event_loop()
    video_path = await loop.run_in_executor(None, lambda: asyncio.run(download_video(url, user_id))) if asyncio.iscoroutine(download_video(url, user_id)) else await download_video(url, user_id)
    
    if video_path and os.path.exists(video_path):
        try:
            with open(video_path, 'rb') as video_file:
                await update.message.reply_video(video=video_file, caption="فەرموو، ڤیدیۆیا تە ئامادەیە ✨\nBy: Tech Ai")
            await status_msg.delete()
        except Exception as e:
            await update.message.reply_text(f"ببورە، کێشەیەک هەبوو د فڕێکرنا ڤیدیۆیێ دا: {e}")
        
        if os.path.exists(video_path): os.remove(video_path)
    else:
        await update.message.reply_text("ببورە، من نەشیا ڤێ ڤیدیۆیێ داونلود بکەم. دڵنیابە کو لینکێ تە یێ دروستە و ڤیدیۆیا وی پوبلیکە.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
