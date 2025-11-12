import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from src.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

async def chatid_command(update: Update, context: CallbackContext):
    """
    Responds to the /chatid command by sending the chat ID,
    if the user is an administrator of the chat.
    """
    chat = update.effective_chat
    user = update.effective_user

    if not chat or not user:
        logging.warning("Could not get chat or user from update.")
        return

    if chat.type in ['group', 'supergroup']:
        try:
            chat_member = await context.bot.get_chat_member(chat.id, user.id)
            if chat_member.status not in ['administrator', 'creator']:
                logging.info(f"User {user.id} is not an admin in chat {chat.id}. Ignoring /chatid command.")
                return
        except Exception as e:
            logging.error(f"Could not verify admin status for user {user.id} in chat {chat.id}: {e}")
            return

    message = f"This chat's ID is: `{chat.id}`"
    await update.message.reply_text(message, parse_mode='MarkdownV2')
    logging.info(f"Sent chat ID {chat.id} to chat.")

def main():
    """
    Starts the bot to listen for the /chatid command.
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        logging.error("Error: TELEGRAM_BOT_TOKEN not set in environment variables.")
        return

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("chatid", chatid_command))

    application.run_polling()

if __name__ == "__main__":
    logging.info("Starting bot to listen for /chatid command...")
    main()
