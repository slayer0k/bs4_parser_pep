import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if not response:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    main_div = find_tag(
        soup, 'section', attrs={'id': 'what-s-new-in-python'}
    )
    div_with_ul = find_tag(
        main_div, 'div', attrs={'class': 'toctree-wrapper'}
    )
    div_with_ul = main_div.find(
        'div', attrs={'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if not response:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        result.append((version_link, h1.text, dl_text))
    return result


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if not response:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(
        soup, 'div', attrs={'class': 'sphinxsidebarwrapper'}
    )
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All version' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Тут ничего нет')
    result = [('Ссылка на документацию', 'Версия', 'Статус')]
    for url in tqdm(a_tags):
        link = url['href']
        pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
        text_match = re.search(pattern, url.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = url.text, ''
        result.append((link, version, status))
    return result


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if not response:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    table_tag = find_tag(
        soup, 'table', attrs={'class': 'docutils'}
    )
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранен в {archive_path}')


def pep(session):
    response = get_response(session, PEP_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    numerical_section = find_tag(
        soup, 'section', attrs={'id': 'numerical-index'}
    )
    table_tag = find_tag(
        numerical_section, 'tbody'
    )
    tr_tags = table_tag.find_all('tr')
    results = {}
    for tr_tag in tqdm(tr_tags):
        status_tag = tr_tag.td
        preview_status = status_tag.text[1:]
        pep_link = find_tag(
            status_tag.find_next_sibling('td'), 'a'
        ).get('href')
        pep_article_url = urljoin(PEP_URL, pep_link)
        response = get_response(session, pep_article_url)
        soup = BeautifulSoup(response.text, 'lxml')
        dl_tag = find_tag(
            soup, 'dl', attrs={'class': 'rfc2822 field-list simple'}
        )
        status = dl_tag.find(string='Status').find_next('dd').abbr.text
        if status in EXPECTED_STATUS[preview_status]:
            results.setdefault(EXPECTED_STATUS[preview_status], 0)
            results[EXPECTED_STATUS[preview_status]] += 1
        else:
            logging.info(
                f'''
                 Несовпадаюшие статусы:
                 {pep_article_url}
                 Статус в карточке: {status}
                 Ожидаемые статусы: {EXPECTED_STATUS[preview_status]}
                '''
            )
            results.setdefault(status, 0)
            results[status] += 1
        final_results = [('Статус', 'Количество')]
        for key, value in results.items():
            final_results.append((key, value))
        final_results.append(('Total', sum(results.values())))
    return final_results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION)
    args = arg_parser.parse_args()
    logging.info(f'аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results:
        control_output(results, args)
    logging.info('Парсер закончил работу')


if __name__ == '__main__':
    main()