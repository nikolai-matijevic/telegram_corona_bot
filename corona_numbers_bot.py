"""
Get daily updates on the current numbers of Infections in your country.
"""

import logging, os, json, time
from requests import request
from requests_cache import install_cache
from emoji import emojize
from telegram.ext import Updater, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

install_cache('covid19api_cache', backend='sqlite', expire_after=600)

api_url = 'https://api.covid19api.com/'
api_summary = api_url + 'summary'


def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M'][magnitude])


def start(update, context):
    update.message.reply_text(
        'Last time updated (UTC)\n\n' + \
        emojize(':earth_americas:: ', use_aliases=True) + 'Global cases\n' + \
        emojize(':mask:: ', use_aliases=True) + 'Infected\n' + \
        emojize(':skull:: ', use_aliases=True) + 'Deceased\n' + \
        emojize(':smiley:: ', use_aliases=True) + 'Recovered\n\n' + \
        'dev@nikolaimatijevic.de\n\nhttps://github.com/nikolai-matijevic/telegram_corona_bot'
    )


def get(update, context):
    response = request("GET", api_summary)
    cases = json.loads(response.text)
    now = time.ctime(int(time.time()))
    logger.debug("Time: {0} / Used Cache: {1}".format(now, response.from_cache))
    print()
    global_cases = cases['Global']

    last_update = cases['Date']
    global_total_confirmed = global_cases['TotalConfirmed']
    global_total_deaths = global_cases['TotalDeaths']
    global_total_recovered = global_cases['TotalRecovered']
    global_total_infected = global_total_confirmed - global_total_recovered - global_total_deaths
    
    update.message.reply_text(
        last_update + '\n\n' + \
        emojize(':earth_americas:: ', use_aliases=True) + human_format(global_total_confirmed) + '\n' + \
        emojize(':mask:: ', use_aliases=True) + human_format(global_total_infected) + '\n' + \
        emojize(':skull:: ', use_aliases=True) + human_format(global_total_deaths) + '\n' + \
        emojize(':smiley:: ', use_aliases=True) + human_format(global_total_recovered))


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    #updater = Updater(os.environ['TOKEN'], use_context=True)
    updater = Updater('1257960258:AAHaKvVgZTfXPQftC3mC0PuXW9La-Q3KkvU', use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("get", get))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
