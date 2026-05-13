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

# --- فەنکشنا نوو بۆ دروستکرنا Line Art یێ پاقژ ---
def process_to_line_art(input_path, output_path):
    # خواندنا وێنەی
    img = cv2.imread(input_path)
    
    # ١. گوهۆڕین بۆ رەنگێ رەش و سپی (Gray)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # ٢. لادانا نویزێ دا کو هێلێن زێدە نەهێن (Noise Reduction)
    blurred = cv2.medianBlur(gray, 5)
    
    # ٣. بکارئینانا Adaptive Thresholding بۆ دروستکرنا هێلێن پاقژ (Coloring Book Style)
    # ئەڤە دێ وێنەی کەتە تەنێ رەش و سپی یێ یەکسان بێ سێبەری
    line_art = cv2.adaptiveThreshold(
        blurred, 255, 
        cv2.ADAPTIVE_THRESH_MEAN_C, 
        cv2.THRESH_BINARY, 
        blockSize=9, 
        C=5
    )
    
    # ٤. پاقژکرنا دوماهیێ بۆ زێدەکرنا کنتراستی
    cv2.imwrite(output_path, line_art)

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
        "بخێر بێی بۆ بوتێ دروستکرنا وێنەی ب شێوازێ Line Art 🎨\n\nبۆ دەستپێکرن، پێدویستە ببیتە ئەندام د کەناڵێ مە دا:\n" + CHANNEL_URL,
        reply_markup=reply_markup
    )

# پشکنین ب رێکا دوگمێ
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await check_sub(update, context):
        await query.edit_message_text("سوپاس بۆ جوین بوونا تە! نوکە هەر وێنەکێ تە بڤێت فڕێکە دا بکەمە Line Art یێ پاقژ.")
    else:
        await query.message.reply_text("تۆ هێشتا نەبوویە ئەندام! تکایە جوین بکە پاشان کلیک ل پشکنین بکە.")

# وەرگرتن و کارکرن ل سەر وێنەی
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sub(update, context):
        await update.message.reply_text("تکایە سەرەتا جوین بکە: " + CHANNEL_URL)
        return

    msg = await update.message.reply_text("خەریکە هێلێن وێنەی دکێشم... تکایە چاوەڕێ بە ⏳")
    
    try:
        # داونلودکرنا وێنەی
        photo_file = await update.message.photo[-1].get_file()
        input_file = f"{update.effective_user.id}_input.jpg"
        output_file = f"{update.effective_user.id}_lineart.png" # ب png پاقژترە
        await photo_file.download_to_drive(input_file)

        # گوهۆرینا وێنەی
        process_to_line_art(input_file, output_file)

        # فڕێکرنا وێنەیێ نوو
        with open(output_file, 'rb') as photo:
            await update.message.reply_photo(
                photo, 
                caption="ئەڤە ژی وێنێ تە ب شێوازێ Line Art ✨\n(Black & White, Clean Lines)"
            )
            
        await msg.delete() # لادانا نامەیا چاوەڕێ بە

    except Exception as e:
        await update.message.reply_text("ببورە، کێشەیەک د دروستکرنا وێنەی دا هەبوو.")
        logging.error(f"Error: {e}")

    # پاقژکرنا فایلان
    if os.path.exists(input_file): os.remove(input_file)
    if os.path.exists(output_file): os.remove(output_file)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
