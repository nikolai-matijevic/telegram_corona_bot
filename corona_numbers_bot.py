"""
Get daily updates on the current numbers of Infections in your country.
"""

import logging, os, json, time
import requests
from requests_cache import install_cache
from emoji import emojize
from emoji import EMOJI_UNICODE
from telegram.ext import Updater, CommandHandler
import telegram.bot
from telegram.ext import messagequeue as mq
from telegram.ext import MessageHandler, Filters
from telegram.utils.request import Request


class MQBot(telegram.bot.Bot):
    '''A subclass of Bot which delegates send method handling to MQ'''
    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        '''Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments'''
        return super(MQBot, self).send_message(*args, **kwargs)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('bot.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


install_cache('covid19api_cache', backend='sqlite', expire_after=60)

api_url = 'https://api.covid19api.com/'
api_summary = api_url + 'summary'
api_countries = api_url + 'countries'


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
    response = requests.request("GET", api_summary)
    cases = json.loads(response.text)
    now = time.ctime(int(time.time()))

    logger.debug("Time: {0} / Used Cache: {1}".format(now, response.from_cache))

    return cases


def display_numbers(location, flag, last_update, total_confirmed, total_infected, total_deaths, total_recovered):
    return str(
        location + ' - ' + last_update + ' (UTC)\n\n' + \
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
        'Get country specific numbers by using the two character country code:\n https://www.iban.com/country-codes\n\n' + \
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
    
    update.message.reply_text(display_numbers('Global', ':earth_americas:: ', last_update, global_total_confirmed, global_total_infected, global_total_deaths, global_total_recovered))


def get_country(update, context):
    cases = request_global_numbers()

    iso2 = str(context.args[0])
    iso2 = str.upper(iso2)

    country = search_country(cases, iso2)

    if country == None:
        country_not_found(update, context)

    last_update = cases['Date']

    total_confirmed = country['TotalConfirmed']
    total_deaths = country['TotalDeaths']
    total_recovered = country['TotalRecovered']
    total_infected = total_confirmed - total_recovered - total_deaths

    flag = search_country_flag(country['Country'])

    update.message.reply_text(display_numbers(country['Country'], flag, last_update, total_confirmed, total_infected, total_deaths, total_recovered))


def list_countries(update, context):
    list_of_countries = ""
    
    cases = request_global_numbers()

    countries = cases['Countries']

    for country in countries:
        list_of_countries = list_of_countries + str("{} - {}\n").format(country['CountryCode'], country['Country'])

    update.message.reply_text(list_of_countries)


def search_country(cases, country_code):
    countries = cases['Countries']

    for country in countries:
        if country['CountryCode'] == country_code:
            return country
    
    logger.warn("Unable to find country for country code {}".format(country_code))

    return None


def country_not_found(update, context):
    chatid = update.message.chat_id
    context.bot.send_message(chat_id=chatid, text=(emojize(':disappointed_face: ', use_aliases=True) + "Country not found. Probably no numbers available."))
    # update.message.reply_text(emojize(':disappointed_face: ', use_aliases=True) + "Country not found. Probably no numbers available.")


def search_country_flag(country):
    country = country.replace(" ", "_")
    country = country.replace("and", "&")

    for key in EMOJI_UNICODE:
        if key == (':' + country + ':'):
            return EMOJI_UNICODE[key] + ': '
    
    return ':question_mark:: '


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text(emojize(':warning: ', use_aliases=True) + " Unable to fulfil request.")


if __name__ == '__main__':
    q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
    request = Request(con_pool_size=8)

    bot = MQBot(token, request=request, mqueue=q)

    updater = Updater(bot=bot, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("get", get, pass_args=True))
    dp.add_handler(CommandHandler("list", list_countries))


    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()