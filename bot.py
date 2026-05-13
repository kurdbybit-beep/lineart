import logging
import cv2
import numpy as np
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- ڕێکخستن (Settings) ---
TOKEN = "8653100665:AAENWuUmSpHex5cckLycNmyoDIDwjGdMGgI"
CHANNEL_URL = "https://t.me/tech_ai_falah"
CHANNEL_ID = "@tech_ai_falah"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- فەنکشنا دروستکرنا Line Art (وەک وێنەی نموونە) ---
def process_to_line_art(input_path, output_path):
    img = cv2.imread(input_path)
    if img is None: return False
    
    # 1. گۆڕین بۆ ڕەنگی خۆڵەمێشی
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. لووسکردنی وێنەکە بۆ لادانی سێبەر و نویز
    smooth = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # 3. دۆزینەوەی هێڵەکان (Canny)
    edges = cv2.Canny(smooth, 50, 150)
    
    # 4. ئەستوورکردنی هێڵەکان بۆ ئەوەی وەک وێنە نموونەییەکە بێت
    kernel = np.ones((2, 2), np.uint8)
    thick_edges = cv2.dilate(edges, kernel, iterations=1)
    
    # 5. سپیکردنی پشتخلف و ڕەشکردنی هێڵەکان
    line_art = cv2.bitwise_not(thick_edges)
    
    cv2.imwrite(output_path, line_art)
    return True

# فەنکشنا پشکنینا جوین بوونێ
async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False

# فەرمانا Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("Join Channel | کەناڵ", url=CHANNEL_URL)],
        [InlineKeyboardButton("Check | من جوین کر ✅", callback_data='check_sub')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"سڵاو {user_name} خێرهاتی بۆ بوتێ Line Art 🎨\n\nبۆ کارکردن تکایە سەرەتا ببە ئەندام لە کەناڵ، پاشان کلیک لە 'من جوین کر' بکە.",
        reply_markup=reply_markup
    )

# پشکنین ب رێکا دوگمێ
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    if await is_subscribed(user_id, context):
        await query.edit_message_text("سوپاس! نوکە هەر وێنەکێ تە بڤێت فڕێکە دا بۆ بکەمە Line Art یێ پاقژ.")
    else:
        await query.message.reply_text("تۆ هێشتا نەبوویە ئەندام! تکایە جوین بکە پاشان کلیک ل پشکنین بکە.")

# وەرگرتن و کارکرن ل سەر وێنەی
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await is_subscribed(user_id, context):
        await update.message.reply_text(f"ببورە، پێویستە سەرەتا جوین ببیت:\n{CHANNEL_URL}")
        return

    msg = await update.message.reply_text("خەریکم هێڵەکان دەکێشم... ⏳")
    
    input_file = f"in_{user_id}.jpg"
    output_file = f"out_{user_id}.png"
    
    try:
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive(input_file)

        if process_to_line_art(input_file, output_file):
            with open(output_file, 'rb') as photo:
                await update.message.reply_photo(photo, caption="فەرموو، Line Art ئامادەیە ✨")
            await msg.delete()
        else:
            await update.message.reply_text("هەڵەیەک لە خوێندنەوەی وێنەکە هەبوو.")
            
    except Exception as e:
        await update.message.reply_text("کێشەیەک دروست بوو.")
        logging.error(f"Error: {e}")

    if os.path.exists(input_file): os.remove(input_file)
    if os.path.exists(output_file): os.remove(output_file)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Bot is Running...")
    app.run_polling()

if __name__ == '__main__':
    main()
