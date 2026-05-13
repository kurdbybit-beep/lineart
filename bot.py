import logging
import cv2
import numpy as np
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- تنظیمات ---
TOKEN = "8653100665:AAENWuUmSpHex5cckLycNmyoDIDwjGdMGgI"
CHANNEL_URL = "https://t.me/tech_ai_falah"
CHANNEL_ID = "@tech_ai_falah"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- فەنکشنا پاقژکرنا وێنەی (Coloring Book Style) ---
def process_to_line_art(input_path, output_path):
    img = cv2.imread(input_path)
    if img is None: return False
    
    # 1. گوهۆرین بۆ رەش و سپی
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. ئینڤێرت کرن (پێچەوانەکرن)
    inverted = 255 - gray
    
    # 3. لێڵکرن (Blur) بۆ لادانا سێبەر و رەنگێن ناڤ وێنەی
    blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
    
    # 4. تێکەڵکرن (Dodge) بۆ دروستکرنا هێڵێن پاقژ
    # ئەڤ هەنگاڤە وێنەی رێک دکەتە وەک وێنەیێ تە نیشان دای
    inverted_blurred = 255 - blurred
    sketch = cv2.divide(gray, inverted_blurred, scale=256.0)
    
    # 5. زێدەکرنا کنتراستی دا کو هێڵ تەمام رەش بن و ناڤ سپی بیت
    _, result = cv2.threshold(sketch, 240, 255, cv2.THRESH_BINARY)
    
    cv2.imwrite(output_path, result)
    return True

# پشکنینا جوین بوونێ
async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Join Channel | کەناڵ", url=CHANNEL_URL)],
        [InlineKeyboardButton("Check | من جوین کر ✅", callback_data='check_sub')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "خێرهاتی! وێنەیێ خۆ بفرێژە دا بکەمە Line Art یێ پاقژ (بۆ رەنگکرنێ) 🎨",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_subscribed(query.from_user.id, context):
        await query.edit_message_text("تۆ سەرکەفتی! نوکە وێنەی بفرێژە.")
    else:
        await query.message.reply_text("تکایە سەرەتا جوین بکە پاشان کلیک ل پشکنین بکە.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        await update.message.reply_text(f"سەرەتا جوین بکە:\n{CHANNEL_URL}")
        return

    msg = await update.message.reply_text("خەریکە وێنەی پاقژ دکەم... ⏳")
    input_file = f"in_{user_id}.jpg"
    output_file = f"out_{user_id}.png"
    
    try:
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive(input_file)

        if process_to_line_art(input_file, output_file):
            with open(output_file, 'rb') as photo:
                await update.message.reply_photo(photo, caption="ئەڤە ژی وێنەیێ تە ب شێوازێ Line Art ✨")
            await msg.delete()
        else:
            await update.message.reply_text("کێشەیەک د وێنەی دا هەبوو.")
    except Exception as e:
        logging.error(f"Error: {e}")

    if os.path.exists(input_file): os.remove(input_file)
    if os.path.exists(output_file): os.remove(output_file)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == '__main__':
    main()
