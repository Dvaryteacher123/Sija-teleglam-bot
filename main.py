import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Sanidi logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Dictionary ya kuhifadhi maonyo ya kila mtumiaji
warnings = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_url = "https://res.cloudinary.com/dvbftux6w/image/upload/v1782940328/yt8vqnuybzly1jhgv9nq.png"
    caption = "Karibu! Mimi ni Protector Bot.\n\nNitafuta link zozote zinazotumwa kwenye group.\n- Onyo 1 & 2: Ujumbe utafutwa.\n- Onyo 3: Utaondolewa (Kick)."
    
    keyboard = [
        [InlineKeyboardButton("WhatsApp Channel", url="https://whatsapp.com/channel/0029VbCRC9b5fM5cruU8PF2M")],
        [InlineKeyboardButton("Telegram Channel", url="https://t.me/+nxAx-q0RRLJmOTBk")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_photo(photo=photo_url, caption=caption, reply_markup=reply_markup)

async def protect_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Angalia kama ujumbe una link
    if update.message and (update.message.entities or update.message.caption_entities):
        entities = update.message.entities or update.message.caption_entities
        has_link = any(e.type in ['url', 'text_link'] for e in entities)
        
        if has_link:
            user = update.effective_user
            chat_id = update.effective_chat.id
            user_id = user.id
            
            # Futa ujumbe
            await update.message.delete()
            
            # Ongeza onyo
            warnings[user_id] = warnings.get(user_id, 0) + 1
            count = warnings[user_id]
            
            if count < 3:
                msg = await context.bot.send_message(chat_id, f"⚠️ {user.first_name}, links are not allowed! (Warning {count}/3)")
                # Futa onyo baada ya sekunde 5
                context.job_queue.run_once(lambda context, m=msg: context.bot.delete_message(m.chat_id, m.message_id), 5)
            else:
                await context.bot.send_message(chat_id, f"🚫 {user.first_name} removed for spamming links.")
                await context.bot.ban_chat_member(chat_id, user_id)
                await context.bot.unban_chat_member(chat_id, user_id)
                warnings[user_id] = 0

if __name__ == '__main__':
    import os
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    # Inasikiliza link kwenye groups
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & (filters.Entity("url") | filters.Entity("text_link")), protect_group))
    
    print("Protector Bot imewaka...")
    app.run_polling()

