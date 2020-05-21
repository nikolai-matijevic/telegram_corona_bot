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
    update.message.reply_text('Requesting current stats...')
    with urllib.request.urlopen(api_url) as url:
        cases = json.loads(url.read().decode())
        global_cases = cases['Global']
    
        global_total_confirmed = global_cases['TotalConfirmed']
        global_total_deaths = global_cases['TotalDeaths']
        global_total_recovered = global_cases['TotalRecovered']
        
        update.message.reply_text(
            'Total: ' + f'{global_total_confirmed:,}' + '\n' + \
            'Deceased: ' + f'{global_total_deaths:,}' + '\n' + \
            'Recovered: ' + f'{global_total_recovered:,}')


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
