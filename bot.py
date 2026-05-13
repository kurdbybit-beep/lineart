import logging
import cv2
import numpy as np
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- تنظیمات ---
TOKEN = "8653100665:AAENWuUmSpHex5cckLycNmyoDIDwjGdMGgI"
CHANNEL_URL = "https://t.me/tech_ai_falah"
CHANNEL_ID = "@tech_ai_falah" # ناسناما کەناڵی (پێدویستە بوت لێ ئەدمین بیت)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# فەنکشنا گوهۆرینا وێنەی بۆ Line Art
def process_to_line_art(input_path, output_path):
    img = cv2.imread(input_path)
    # گوهۆرین بۆ رەنگێ رەش و سپی
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # لادانا نویز و لێلکرن
    inverted_gray = 255 - gray
    blurred = cv2.GaussianBlur(inverted_gray, (21, 21), 0)
    inverted_blurred = 255 - blurred
    # دروستکرنا شێوازێ قەلەم (Pencil Sketch/Line Art)
    sketch = cv2.divide(gray, inverted_blurred, scale=256.0)
    cv2.imwrite(output_path, sketch)

# فەنکشنا پشکنینا جوین بوونێ
async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False

# فەرمانا Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Join Channel | چوونەناڤ کەناڵی", url=CHANNEL_URL)],
                [InlineKeyboardButton("Check | پشکنین", callback_data='check_sub')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "بۆ بکارئینانا ڤی بوتی، پێدویستە سەرەتا ببیتە ئەندام د کەناڵێ مە دا:\n" + CHANNEL_URL,
        reply_markup=reply_markup
    )

# پشکنین ب رێکا دوگمێ
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await check_sub(update, context):
        await query.edit_message_text("سوپاس بۆ جوین بوونا تە! نوکە هەر وێنەکێ تە بڤێت فڕێکە دا بکەمە Line Art.")
    else:
        await query.message.reply_text("تۆ هێشتا نەبوویە ئەندام! تکایە جوین بکە پاشان کلیک ل پشکنین بکە.")

# وەرگرتن و کارکرن ل سەر وێنەی
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sub(update, context):
        await update.message.reply_text("تکایە سەرەتا جوین بکە: " + CHANNEL_URL)
        return

    await update.message.reply_text("ل هیڤیێ بە... وێنێ تە دهێتە دروستکرن 🎨")
    
    # داونلودکرنا وێنەی
    photo_file = await update.message.photo[-1].get_file()
    input_file = f"{update.effective_user.id}_input.jpg"
    output_file = f"{update.effective_user.id}_lineart.jpg"
    await photo_file.download_to_drive(input_file)

    # گوهۆرینا وێنەی
    process_to_line_art(input_file, output_file)

    # فڕێکرنا وێنەیێ نوو
    with open(output_file, 'rb') as photo:
        await update.message.reply_photo(photo, caption="ئەڤە ژی وێنێ تە ب شێوازێ Line Art ✨")

    # پاقژکرنا فایلان
    os.remove(input_file)
    os.remove(output_file)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
