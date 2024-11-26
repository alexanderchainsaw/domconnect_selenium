from dataclasses import dataclass
from lxml.etree import XPath
from lxml.etree import XPathSyntaxError


@dataclass
class XPaths:
    OPEN_LOGIN_MENU: str = '//*[@data-role="login"]'
    EMAIL_INPUT: str = '//*[@name="email"]'
    PASSWORD_INPUT: str = '//*[@name="password"]'
    LOGIN_SUBMIT: str = "//button[@type='submit' and text()='Войти']"
    PROXIES_TABLE: str = "//table[@class='table user_proxy_table']"
    PROXIES_TABLE_ELEMENT: str = './/tr[contains(@id,"el-")]'
    IP_PORT: str = ".//div[@class='right clickselect ']"
    EXPIRATION_DATE: str = ".//div[@class='right color-success']"

    def __post_init__(self):
        for value in self.__dict__.values():
            try:
                XPath(value)
            except XPathSyntaxError:
                raise RuntimeError(f'Не валидный xpath: {value}')


xpaths = XPaths()
