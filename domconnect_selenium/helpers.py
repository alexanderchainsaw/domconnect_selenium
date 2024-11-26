import re
from datetime import datetime
import time
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from xpaths import xpaths
import logging

logger = logging.getLogger(__name__)


def first_captcha_routine(
        login_submit_button: WebElement,
        max_attempts: int = 10
) -> None:

    attempts = 0
    while attempts < max_attempts:
        logger.debug(f'Ждем 10 секунд перед нажатием, попытка {attempts + 1}/{max_attempts}')
        time.sleep(10)
        try:
            logger.debug('Пытаемся нажать на кнопку логина')
            login_submit_button.click()
            logger.info('Кнопка логина нажата!')
            return
        except selenium.common.exceptions.ElementClickInterceptedException:
            logger.debug('Клик перехвачен, предполагаем что капча еще не заполнена')
            pass
        attempts += 1
    else:
        raise RuntimeError(f'Больше {max_attempts} попыток нажать на кнопку логина, видимо что-то не так!')


def second_captcha_routine(
        driver: webdriver.Chrome,
        login_submit_button: WebElement,
        max_attempts: int = 10
) -> WebElement:

    attempts = 0
    while attempts < max_attempts:
        try:
            logger.debug(f'Ждём появления таблицы с прокси, при ненахождении пытаемся нажать на кнопку входа '
                         f'попытка {attempts + 1}/{max_attempts}')
            table_of_proxies = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, xpaths.PROXIES_TABLE)))
            logger.info('Таблица с прокси найдена!')
            return table_of_proxies
        except selenium.common.exceptions.TimeoutException:
            logger.debug('Пытаемся нажать на кнопку логина')
            login_submit_button.click()
            logger.debug('Кнопка логина нажата!')
    else:
        raise RuntimeError(f'Больше {max_attempts} попыток нажать на кнопку логина, '
                           f'видимо что-то не так! (вторая капча)')


def validate_ip_port(value: str) -> bool:
    if ':' not in value:
        return False
    if len(value.split(':')) != 2:
        return False
    ip, port = value.split(':')
    if not port.isdigit():
        return False
    if int(port) not in range(1, 65536):
        return False

    return bool(re.fullmatch(r"^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.)"
                             r"{3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$", ip))


def validate_date_time(value: str) -> bool:
    date_time = value.split(', ')
    if len(date_time) != 2:
        return False
    ddmmyy = date_time[0].split('.')
    if len(ddmmyy) != 3:
        return False
    if len(ddmmyy[2]) == 2:
        ddmmyy[2] = f"20{ddmmyy[2]}"  # добавляем 20 к году чтобы получится четырёхзначный год
        value = f"{'.'.join(ddmmyy)}, {date_time[1]}"

    # пытаемся конвертировать дату и время в объект datetime, при неудаче возвращаем False
    try:
        datetime.strptime(value, '%d.%m.%Y, %H:%M')
        return True
    except ValueError:
        return False
