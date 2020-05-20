"""
Get daily updates on the current numbers of Infections in your country.
"""

import logging, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')


def setup(update, context):
    """Start bot setup."""
    update.message.reply_text('Let\'s set you up!')


def corona_status(context):
    job = context.job
    context.bot.send_message(job.context, text='Beep!')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(os.environ['TOKEN'], use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setup", setup))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
