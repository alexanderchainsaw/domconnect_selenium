import time
import sys
import re
import os
from datetime import datetime
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

LOGIN_INIT_XPATH = '//*[@data-role="login"]'  # путь к кнопке открытия окна входа
EMAIL_INPUT_XPATH = '//*[@name="email"]'  # путь к полю ввода email
PASSWORD_INPUT_XPATH = '//*[@name="password"]'  # путь к полю ввода пароля
LOGIN_SUBMIT_XPATH = "//button[@type='submit' and text()='Войти']"   # путь к кнопке подтверждения реквизитов для входа
PROXIES_TABLE_XPATH = "//table[@class='table user_proxy_table']"  # путь к таблице с прокси
PROXIES_TABLE_ELEMENT_XPATH = './/tr[contains(@id,"el-")]'  # путь к элементу таблицы с прокси
IP_PORT_XPATH = ".//div[@class='right clickselect ']"  # путь к элементу который содержит ip:port прокси
EXPIRATION_DATE_XPATH = ".//div[@class='right color-success']"  # путь к элементу который содержит срок истечения прокси

load_dotenv()
email, password = os.getenv('EMAIL'), os.getenv('PASSWORD')


def _validate_ip_port(value: str) -> bool:
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


def _validate_date_time(value: str) -> bool:
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


def main():
    browser = webdriver.Chrome(service=Service(executable_path='chromedriver-win64/chromedriver.exe'))

    # открываем страницу сайта
    browser.get('https://proxy6.net/')

    # ждём появления кнопки входа на странице
    login_button = WebDriverWait(browser, 10).until(EC.presence_of_element_located(
        (By.XPATH, LOGIN_INIT_XPATH)))

    # ждём кликабельности кнопки входа и сразу же кликаем
    WebDriverWait(browser, 10).until(EC.element_to_be_clickable(login_button)).click()

    # ждём появления области ввода для email и области ввода пароля
    email_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located(
        (By.XPATH, EMAIL_INPUT_XPATH)))
    password_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located(
        (By.XPATH, PASSWORD_INPUT_XPATH)))

    # вставляем наши реквизиты для входа
    email_field.send_keys(email)
    password_field.send_keys(password)

    login_submit_button = WebDriverWait(browser, 10).until(EC.presence_of_element_located(
        (By.XPATH, LOGIN_SUBMIT_XPATH)))

    # Здесь мы вручную заполняем капчу, скрипт будет пытатся нажать на кнопку логина каждые 10 секунд
    attempts = 0
    max_attempts = 10
    while attempts < max_attempts:
        logger.info(f'Ждем 10 секунд перед нажатием, попытка {attempts + 1}/{max_attempts}')
        time.sleep(10)
        try:
            logger.info('Пытаемся нажать на кнопку логина')
            login_submit_button.click()
            logger.info('Кнопка логина нажата!')
            break
        except selenium.common.exceptions.ElementClickInterceptedException:
            logger.info('Клик перехвачен, предполагаем что капча еще не заполнена')
            pass
        attempts += 1
    else:
        raise RuntimeError(f'Больше {max_attempts} попыток нажать на кнопку логина, видимо что-то не так!')

    logger.info('Ждём появления таблицы с прокси (ждем 60 секунд на случай если появилась дополнительная капча)')
    table_of_proxies = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.XPATH, PROXIES_TABLE_XPATH)))

    result = []

    # итерируем по панелям с прокси (в каждой панели информация об этом прокси)
    for row in table_of_proxies.find_elements(By.XPATH, PROXIES_TABLE_ELEMENT_XPATH):
        ip_port = row.find_element(By.XPATH, IP_PORT_XPATH).text.strip()
        expiration_date = row.find_element(By.XPATH, EXPIRATION_DATE_XPATH).text.strip()

        if not _validate_ip_port(ip_port):
            raise ValueError(f'Не пройдена валидация: {ip_port}')
        if not _validate_date_time(expiration_date):
            raise ValueError(f'Не пройдена валидация: {expiration_date}')

        result.append(f"{ip_port} - {expiration_date}")
        logger.info(f'Успешно собрали данные: {ip_port} - {expiration_date}')

    for el in result:
        print(el)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
