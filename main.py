import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Warnings storage: {user_id: count}
warnings = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_url = "https://res.cloudinary.com/dvbftux6w/image/upload/v1782940328/yt8vqnuybzly1jhgv9nq.png"
    caption = (
        "Hello! I am your Group Protector Bot.\n\n"
        "I am here to keep this group clean by automatically deleting any links sent.\n\n"
        "Rules:\n"
        "1. Links are strictly prohibited.\n"
        "2. 1st & 2nd offense: Message will be deleted.\n"
        "3. 3rd offense: You will be removed from the group."
    )
    
    await update.message.reply_photo(photo=photo_url, caption=caption)

async def protect_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and (update.message.entities or update.message.caption_entities):
        entities = update.message.entities or update.message.caption_entities
        has_link = any(e.type in ['url', 'text_link'] for e in entities)
        
        if has_link:
            user = update.effective_user
            chat_id = update.effective_chat.id
            user_id = user.id
            
            # Delete the message
            await update.message.delete()
            
            # Count warnings
            warnings[user_id] = warnings.get(user_id, 0) + 1
            count = warnings[user_id]
            
            if count < 3:
                msg = await context.bot.send_message(
                    chat_id, 
                    f"⚠️ {user.first_name}, links are not allowed here! (Warning {count}/3)"
                )
                # Delete warning message after 5 seconds
                context.job_queue.run_once(lambda context, m=msg: context.bot.delete_message(m.chat_id, m.message_id), 5)
            else:
                await context.bot.send_message(chat_id, f"🚫 {user.first_name} has been removed for spamming links.")
                await context.bot.ban_chat_member(chat_id, user_id)
                await context.bot.unban_chat_member(chat_id, user_id) # Optional: allows them to rejoin later
                warnings[user_id] = 0

if __name__ == '__main__':
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    # Listen for links in groups only
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & (filters.Entity("url") | filters.Entity("text_link")), protect_group))
    
    print("Protector Bot is running...")
    app.run_polling()

