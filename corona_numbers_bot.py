"""
Get daily updates on the current numbers of Infections in your country.
"""

import logging, os, json, urllib.request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

api_url = 'https://api.covid19api.com/summary'


def get(update, context):
    with urllib.request.urlopen(api_url) as url:
        cases = json.loads(url.read().decode())
        global_cases = cases['Global']
    
        global_total_confirmed = str(global_cases['TotalConfirmed'])
        global_total_deaths = str(global_cases['TotalDeaths'])
        global_total_recovered = str(global_cases['TotalRecovered'])
        
        update.message.reply_text('Worldwide infections: ' + global_total_confirmed)
        update.message.reply_text('Worldwide deaths: ' + global_total_deaths)
        update.message.reply_text('Worldwide recoveries: ' + global_total_recovered)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(os.environ['TOKEN'], use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("get", get))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
