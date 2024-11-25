from domconnect_selenium.helpers import validate_date_time, validate_ip_port
from main import email, password


def test_credentials():
    """Проверяем присутствие данных для входа"""
    assert email
    assert password


def test_ip_port_validation():
    assert not validate_ip_port('asdfghjkl')
    assert not validate_ip_port('a.a.a.a:aaaa')
    assert not validate_ip_port('1.1.1:1')
    assert not validate_ip_port('1.1.1.1')
    assert not validate_ip_port('1.1.1.1:')
    assert not validate_ip_port('1245.1.1.1:1')
    assert not validate_ip_port('1.1.1.a:1')
    assert not validate_ip_port('')
    assert not validate_ip_port('0.0.0.0:0')
    assert not validate_ip_port('01.06.012.03:12')

    assert validate_ip_port('0.0.0.0:1')
    assert validate_ip_port('123.123.123.123:30000')


def test_datetime_validation():
    assert validate_date_time('12.05.25, 12:56')
    assert validate_date_time('12.05.2025, 12:56')
    assert validate_date_time('12.05.2025, 0:56')
    assert validate_date_time('1.1.2025, 0:56')
    assert validate_date_time('1.1.25, 0:56')

    assert not validate_date_time('12.05.25, 12:60')
    assert not validate_date_time('0.05.2025, 24:56')
    assert not validate_date_time('12.0.2025, 0:56')
    assert not validate_date_time('1.00.2025, 0:56')
    assert not validate_date_time('1.1.5, 0:56')
    assert not validate_date_time('11.11.25')
    assert not validate_date_time('11.11.2025')
    assert not validate_date_time('')
