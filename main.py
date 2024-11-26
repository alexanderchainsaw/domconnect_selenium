import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from domconnect_selenium import xpaths
from domconnect_selenium import validate_date_time, validate_ip_port, second_captcha_routine, first_captcha_routine
from loguru import logger


load_dotenv()
email, password = os.getenv('EMAIL'), os.getenv('PASSWORD')


def main():
    driver = webdriver.Chrome(service=Service(executable_path='chromedriver-win64/chromedriver.exe'))

    logger.info('Открываем сайт')
    driver.get('https://proxy6.net/')

    logger.debug('Ждём появления кнопки открытия окна входа и кликаем её')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.XPATH, xpaths.OPEN_LOGIN_MENU))).click()

    logger.debug('Ждём появления области ввода для email и области ввода пароля')
    email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, xpaths.EMAIL_INPUT)))
    password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, xpaths.PASSWORD_INPUT)))

    logger.debug('Вставляем наши реквизиты для входа')
    email_field.send_keys(email)
    password_field.send_keys(password)

    logger.debug('Ищём кнопку для входа в аккаунт')
    login_submit_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, xpaths.LOGIN_SUBMIT)))

    logger.info('Ожидаем заполнения капчи')
    if not (table_of_proxies := first_captcha_routine(driver, login_submit_button)):
        logger.info('Ищем элемент после успешного входа в аккаунт (возможна вторая капча)')
        table_of_proxies = second_captcha_routine(driver, login_submit_button)

    result = []

    logger.info('Начинаем поиск нужных данных')
    for row in table_of_proxies.find_elements(By.XPATH, xpaths.PROXIES_TABLE_ELEMENT):
        ip_port = row.find_element(By.XPATH, xpaths.IP_PORT).text.strip()
        expiration_date = row.find_element(By.XPATH, xpaths.EXPIRATION_DATE).text.strip()

        if not validate_ip_port(ip_port):
            raise ValueError(f'Не пройдена валидация: {ip_port}')
        if not validate_date_time(expiration_date):
            raise ValueError(f'Не пройдена валидация: {expiration_date}')

        result.append(f"{ip_port} - {expiration_date}")
        logger.success(f'Успешно собрали данные: {ip_port} - {expiration_date}')

    for el in result:
        print(el)


if __name__ == '__main__':
    main()
