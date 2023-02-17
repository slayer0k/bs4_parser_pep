import logging

from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import NotResponded, ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException as error:
        raise NotResponded(
            f'при обращении к [{url}] произошла ошибка: [{error}]'
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def making_soup(session, url):
    response = get_response(session, url)
    return BeautifulSoup(response.text, 'lxml')
