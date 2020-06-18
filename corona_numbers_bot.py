"""
Get daily updates on the current numbers of Infections in your country.
"""

import logging, os, json, time
from requests import request
from requests_cache import install_cache
from emoji import emojize
from emoji import EMOJI_UNICODE
from telegram.ext import Updater, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

install_cache('covid19api_cache', backend='sqlite', expire_after=600)

api_url = 'https://api.covid19api.com/'
api_summary = api_url + 'summary'


secrets_file = 'secrets_file.json'

token = ""

with open(secrets_file, 'r') as f:
    bot_secrets = json.loads(f.read())
    token = bot_secrets['TELEGRAM_BOT_TOKEN']


def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M'][magnitude])


def request_global_numbers():
    response = request("GET", api_summary)
    cases = json.loads(response.text)
    now = time.ctime(int(time.time()))
    logger.debug("Time: {0} / Used Cache: {1}".format(now, response.from_cache))

    return cases


def display_numbers(flag, last_update, total_confirmed, total_infected, total_deaths, total_recovered):
    return str(
        last_update + ' (UTC)\n\n' + \
        emojize(flag, use_aliases=True) + human_format(total_confirmed) + '\n' + \
        emojize(':mask:: ', use_aliases=True) + human_format(total_infected) + '\n' + \
        emojize(':skull:: ', use_aliases=True) + human_format(total_deaths) + '\n' + \
        emojize(':smiley:: ', use_aliases=True) + human_format(total_recovered)
    )


def start(update, context):
    update.message.reply_text(
        'Last time updated (UTC)\n\n' + \
        emojize(':earth_americas:: ', use_aliases=True) + 'Global cases\n' + \
        emojize(':mask:: ', use_aliases=True) + 'Infected\n' + \
        emojize(':skull:: ', use_aliases=True) + 'Deceased\n' + \
        emojize(':smiley:: ', use_aliases=True) + 'Recovered\n\n' + \
        'Get country specific numbers by using the two character country code:\n /get DE\n\n' + \
        'dev@nikolaimatijevic.de\n\nhttps://github.com/nikolai-matijevic/telegram_corona_bot'
    )
        

def get(update, context):
    if not context.args:
        get_global(update, context)
    else:
        get_country(update, context)


def get_global(update, context):
    cases = request_global_numbers()

    global_cases = cases['Global']

    last_update = cases['Date']
    global_total_confirmed = global_cases['TotalConfirmed']
    global_total_deaths = global_cases['TotalDeaths']
    global_total_recovered = global_cases['TotalRecovered']
    global_total_infected = global_total_confirmed - global_total_recovered - global_total_deaths
    
    update.message.reply_text(display_numbers(':earth_americas:: ', last_update, global_total_confirmed, global_total_infected, global_total_deaths, global_total_recovered))


def get_country(update, context):
    cases = request_global_numbers()

    iso2 = context.args[0]

    country = search_country(cases, iso2)

    last_update = cases['Date']

    total_confirmed = country['TotalConfirmed']
    total_deaths = country['TotalDeaths']
    total_recovered = country['TotalRecovered']
    total_infected = total_confirmed - total_recovered - total_deaths

    flag = search_country_flag(country['Country'])

    update.message.reply_text(display_numbers(flag, last_update, total_confirmed, total_infected, total_deaths, total_recovered))


def search_country(cases, country_code):
    countries = cases['Countries']

    for country in countries:
        if country['CountryCode'] == country_code:
            return country


def search_country_flag(country):
    for key in EMOJI_UNICODE:
        if key == (':' + country + ':'):
            return EMOJI_UNICODE[key] + ': '


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("get", get, pass_args=True))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
