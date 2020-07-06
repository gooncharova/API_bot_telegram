import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = telegram.Bot(token=TELEGRAM_TOKEN)
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

logging.basicConfig(filename='bot_logger.log')
logger = logging.getLogger(__name__)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') is None or homework_name is None:
        logger.error('Отсутствует статус или имя домашки.')
        return 'Отсутствует статус или имя домашки. Нужно проверить.'
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework.get('status') == 'approved':
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему '\
            'уроку.'
    else:
        logger.error('Неизвестный статус.')
        return 'Неизвестный статус. Нужно проверить.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {
        'from_date': current_timestamp
    }
    try:
        homework_statuses = requests.get(url, headers=headers, params=params)
    except requests.exceptions.HTTPError as errh:
        return('Ошибка Http:', errh)
        logger.error('Ошибка Http:', errh)
    except requests.exceptions.ConnectionError as errc:
        return('Соединение не установлено:', errc)
        logger.error('Соединение не установлено:', errc)
    except requests.exceptions.Timeout as errt:
        return('Ошибка тайм-аута:', errt)
        logger.error('Ошибка тайм-аута:', errt)
    except requests.exceptions.RequestException as err:
        return('Случилось что-то еще:', err)
        logger.error('Случилось что-то еще:', err)
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get(
                'current_date')
            time.sleep(1200)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
